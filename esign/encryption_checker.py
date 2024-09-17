import asyncio
import os
import shutil
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
            is_encrypted = await self.check_app_encryption(executable_path, prepared_app_path)
            if is_encrypted:
                self.logger.warning(f"主应用程序已加密: {executable_path}")
            else:
                self.logger.info(f"主应用程序未加密: {executable_path}")

            # 检查插件是否加密
            plugins_dir = os.path.join(prepared_app_path, "PlugIns")
            if os.path.exists(plugins_dir):
                await self.check_plugins_encryption(plugins_dir)

            # 删除 unrestrict
            await self.remove_unrestrict(executable_path)

            return is_encrypted
        except Exception as e:
            raise EncryptionCheckError(f"检测加密状态时发生错误: {str(e)}")

    async def check_app_encryption(self, executable_path: str, prepared_app_path: str) -> bool:
        try:
            otool_path = self.config.get_tool_path('otool')
            cmd = [otool_path, '-l', executable_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise EncryptionCheckError(f"检查加密状态失败: {stderr.decode()}")
            
            output = stdout.decode()
            is_encrypted = 'cryptid 1' in output
            
            return is_encrypted
        except Exception as e:
            raise EncryptionCheckError(f"检查主应用程序加密状态时发生错误: {str(e)}")

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
                            self.logger.warning(f"插件 {plugin} 已加密，将被移除")
                            shutil.rmtree(plugin_path)
        except Exception as e:
            raise EncryptionCheckError(f"检查插件加密状态时发生错误: {str(e)}")
        
    async def remove_unrestrict(self, execu_table_path: str):
        self.logger.info(f"开始删除 unrestrict: {execu_table_path}")
        otool_path = self.config.get_tool_path('otool')
        cmd = [otool_path, 'unrestrict', '-t', execu_table_path]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise EncryptionCheckError(f"删除 unrestrict 失败: {stderr.decode()}")
            
            self.logger.info(f"删除 unrestrict 成功: {stdout.decode()}")
        except Exception as e:
            raise EncryptionCheckError(f"删除 unrestrict 时发生错误: {str(e)}")