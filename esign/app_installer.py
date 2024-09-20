import asyncio
from esign.elogger import Logger
from esign.econfig import ConfigHandler
from esign.exceptions import AppInstallationError

class AppInstaller:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def install(self, app_path: str, install: bool = None, reinstall: bool = None, device_id: str = None):
        try:
            ios_deploy_path = self.config.get_tool_path('ios-deploy_new')
            
            if install:
                cmd = [ios_deploy_path, '-b']
            elif reinstall:
                cmd = [ios_deploy_path, '-rb']
            else:
                raise AppInstallationError("Installation type error")

            cmd.append(app_path)

            if device_id:
                cmd.extend(['--id', device_id])

            cmd.extend(['-W'])
            
            self.logger.info("Installing application")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            async for line in process.stdout:
                self.logger.default(line.decode().strip())
            async for line in process.stderr:
                raise AppInstallationError(f"Installation failed: {line.decode().strip()}")
            await process.wait()
        except Exception as e:
            raise AppInstallationError(f"An error occurred during installation: {str(e)}")