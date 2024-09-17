import asyncio
import os
import plistlib
import subprocess
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import EntitlementsError

class EntitlementsManager:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def process(self, app_path: str, provisioning_profile_path: str):
        try:
            entitlements = await self._extract_entitlements(provisioning_profile_path)
            await self._update_entitlements(entitlements, app_path)
            return entitlements
        except Exception as e:
            raise EntitlementsError(f"处理权限文件失败: {str(e)}")

    async def _extract_entitlements(self, provisioning_profile_path: str) -> dict:
        cmd = f"security cms -D -i {provisioning_profile_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise EntitlementsError(f"提取权限失败: {stderr.decode()}")
        
        plist_data = plistlib.loads(stdout)
        return plist_data.get('Entitlements', {})

    async def _update_entitlements(self, entitlements: dict, app_path: str):
        entitlements_path = os.path.join(app_path, 'entitlements.plist')
        with open(entitlements_path, 'wb') as f:
            plistlib.dump(entitlements, f)
        self.logger.info(f"更新权限文件: {entitlements_path}")