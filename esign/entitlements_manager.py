import asyncio
import os
import plistlib
import shutil
import subprocess
from esign.econfig import ConfigHandler
from esign.eprovision import EProvision
from esign.elogger import Logger
from esign.exceptions import EntitlementsError

class EntitlementsManager:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def _check_provisioning_profile(self, identity: str, provisioning_profile_path: str) -> bool:
        self.provision = EProvision(provisioning_profile_path)
        return self.provision.contain_cer_identity(identity)
        
    async def process(self, identity: str, app_path: str, provisioning_profile_path: str):
        if not await self._check_provisioning_profile(identity, provisioning_profile_path):
            raise EntitlementsError("Certificate and provisioning profile do not match")

        try:
            entitlements = await self._extract_entitlements(provisioning_profile_path)
            # app_entitlements = await self._extract_app_entitlements(app_path)

            # entitlements.update(app_entitlements)
            # for key, value in app_entitlements.items():
            #     if key not in entitlements:
            #         entitlements[key] = value

            entitlements_path = await self._update_entitlements(entitlements)
            shutil.copy(provisioning_profile_path, os.path.join(app_path, 'embedded.mobileprovision'))

            return entitlements_path
        except Exception as e:
            raise EntitlementsError(f"Failed to edit entitlements file: {str(e)}")
        
    async def _extract_app_entitlements(self, app_path: str) -> dict:
        entitlements_path = os.path.join(self.config.get('esign_dir'), 'provision_entitlements.plist')
        if os.path.exists(entitlements_path):
            os.remove(entitlements_path)

        cmd = f"codesign -d --entitlements :- {app_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            self.logger.warning(f"Failed to export entitlements using codesign: {stderr.decode()}")
            # 尝试使用 jtool 导出权限
            jtool2_path = self.config.get_tool_path('jtool2')
            if not os.path.exists(jtool2_path):
                raise EntitlementsError(f"jtool2 tool does not exist: {jtool2_path}")

            cmd = f"{jtool2_path} --ent {app_path} > {entitlements_path}"
            process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise EntitlementsError(f"Failed to export application entitlements: {stderr.decode()}")
        
        with open(entitlements_path, 'wb') as f:
            plistlib.dump(plistlib.loads(stdout), f)

        self.logger.info("Successfully exported app entitlements")
        return plistlib.loads(stdout)

    async def _extract_entitlements(self, provisioning_profile_path: str) -> dict:
        cmd = f"security cms -D -i {provisioning_profile_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise EntitlementsError(f"exported app entitlements fail: {stderr.decode()}")
        
        plist_data = plistlib.loads(stdout)
        return plist_data.get('Entitlements', {})

    async def _update_entitlements(self, entitlements: dict):
        entitlements_path = os.path.join(self.config.get('esign_dir'), 'entitlements.plist')
        if os.path.exists(entitlements_path):
            os.remove(entitlements_path)

        with open(entitlements_path, 'wb') as f:
            plistlib.dump(entitlements, f)
        return entitlements_path