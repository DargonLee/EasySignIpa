import asyncio
import os
import shutil
import subprocess

from esign.elogger import Logger
from esign.econfig import ConfigHandler
from esign.exceptions import EncryptionCheckError

class EncryptionChecker:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def check_encryption(self, executable_path: str, prepared_app_path: str) -> bool:
        try:
            # 检查主应用程序是否加密
            self.logger.info(f"App encryption status:")
            is_encrypted = await self.check_app_encryption(executable_path, prepared_app_path)
            # 检查插件是否加密
            plugins_dir = os.path.join(prepared_app_path, "PlugIns")
            if os.path.exists(plugins_dir):
                await self.check_plugins_encryption(plugins_dir)
            # 检查Frameworks是否加密
            frameworks_dir = os.path.join(prepared_app_path, "Frameworks")
            if os.path.exists(frameworks_dir):
                await self.check_frameworks_encryption(frameworks_dir)
            # 删除 unrestrict
            await self.remove_unrestrict(executable_path)
            return is_encrypted
        except Exception as e:
            raise EncryptionCheckError(f"An error occurred while checking encryption status: {str(e)}")

    async def check_app_encryption(self, executable_path: str, prepared_app_path: str) -> bool:
        try:
            otool_cmd = (
                'otool -l {} | grep cryptid'.format(executable_path)
            )
            otool_cmd_result = subprocess.getoutput(otool_cmd)
            is_encrypted = 'cryptid 1' in otool_cmd_result
            is_invalid_path = any(substring in prepared_app_path for substring in ['PlugIns', 'Frameworks'])
            if is_encrypted and not is_invalid_path:
                raise EncryptionCheckError("The application is encrypted")
            return is_encrypted
        except Exception as e:
            raise EncryptionCheckError(str(e))

    async def check_frameworks_encryption(self, framework_dir: str):
        try:
            for framework in os.listdir(framework_dir):
                framework_path = os.path.join(framework_dir, framework)
                if os.path.isdir(framework_path):
                    framework_executable = os.path.splitext(framework)[0]
                    framework_executable_path = os.path.join(framework_path, framework_executable)
                    if os.path.exists(framework_executable_path):
                        is_encrypted = await self.check_app_encryption(framework_executable_path, framework_dir)
                        if is_encrypted:
                            self.logger.warning(f"Framework encrypted: {framework}")
                        else:
                            self.logger.default(f"Framework not encrypted: {framework} ")
        except Exception as e:
            raise EncryptionCheckError(f"An error occurred while checking the framework encryption status: {str(e)}")
        

    async def check_plugins_encryption(self, plugins_dir: str):
        try:
            for plugin in os.listdir(plugins_dir):
                plugin_path = os.path.join(plugins_dir, plugin)
                if os.path.isdir(plugin_path):
                    plugin_executable = os.path.splitext(plugin)[0]
                    plugin_executable_path = os.path.join(plugin_path, plugin_executable)
                    if os.path.exists(plugin_executable_path):
                        is_encrypted = await self.check_app_encryption(plugin_executable_path, plugins_dir)
                        if is_encrypted:
                            self.logger.warning(f"Plugin encrypted: {plugin} will be removed")
                            shutil.rmtree(plugin_path)
                        self.logger.default(f"PlugIn not encrypted: {plugin} ")
        except Exception as e:
            raise EncryptionCheckError(f"An error occurred while checking the plugin encryption status: {str(e)}")
        
    async def remove_unrestrict(self, execu_table_path: str):
        self.logger.info(f"Deleting unrestrict: {os.path.basename(execu_table_path)}")
        otool_path = self.config.get_tool_path('optool')
        cmd = [otool_path, 'unrestrict', '-t', execu_table_path]
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            self.logger.default(f"Deleting unrestrict result: {stdout.decode().strip()}")
        except Exception as e:
            raise EncryptionCheckError(f"An error occurred while deleting unrestrict: {str(e)}")