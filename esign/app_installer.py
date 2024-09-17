import asyncio
from esign.elogger import Logger
from esign.econfig import ConfigHandler
from esign.exceptions import AppInstallationError

class AppInstaller:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def install(self, app_path: str, install: str = None, device_id: str = None):
        try:
            ios_deploy_path = self.config.get_tool_path('ios_deploy')
            
            if install == 'basic_install':
                cmd = [ios_deploy_path, '-b']
            elif install == 'reinstall':
                cmd = [ios_deploy_path, '-rb']
            else:
                raise AppInstallationError("安装类型错误")

            cmd.append(app_path)

            if device_id:
                cmd.extend(['--id', device_id])
            
            self.logger.info(f"正在安装应用: {app_path}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise AppInstallationError(f"安装失败: {stderr.decode()}")
            
            self.logger.info("应用安装成功")
        except Exception as e:
            raise AppInstallationError(f"安装过程中发生错误: {str(e)}")