import asyncio
import os
import subprocess
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import CodeSigningError

class CodeSigning:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def sign_all(self, app_path: str, identity: str, entitlements_path: str):
        try:
            await self._sign_frameworks(app_path, identity, entitlements_path)
            await self._sign_plugins(app_path, identity, entitlements_path)
            await self._sign_app(app_path, identity, entitlements_path)
        except Exception as e:
            raise CodeSigningError(f"代码签名失败: {str(e)}")

    async def _sign_frameworks(self, app_path: str, identity: str, entitlements_path: str):
        frameworks_path = os.path.join(app_path, 'Frameworks')
        if os.path.exists(frameworks_path):
            for framework in os.listdir(frameworks_path):
                framework_path = os.path.join(frameworks_path, framework)
                await self._codesign(framework_path, identity, entitlements_path)

    async def _sign_plugins(self, app_path: str, identity: str, entitlements_path: str):
        plugins_path = os.path.join(app_path, 'PlugIns')
        if os.path.exists(plugins_path):
            for plugin in os.listdir(plugins_path):
                plugin_path = os.path.join(plugins_path, plugin)
                await self._codesign(plugin_path, identity, entitlements_path)

    async def _sign_app(self, app_path: str, identity: str, entitlements_path: str):
        await self._codesign(app_path, identity, entitlements_path)

    async def _codesign(self, path: str, identity: str, entitlements_path: str, restore_symbol: bool = False):
        # 如果传入了restore_symbol则进行符号化处理
        if restore_symbol:
            from esign.ebin import EBinTool
            EBinTool.restore_symbol(path)

        # 生成签名命令
        cmd = f"codesign -f -s {identity} --entitlements {entitlements_path} {path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise CodeSigningError(f"签名失败 {path}: {stderr.decode()}")
        
        self.logger.info(f"成功签名: {path}")