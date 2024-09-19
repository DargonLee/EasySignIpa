import asyncio
import os
import shutil
import subprocess
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import DylibInjectionError

class DylibInjector:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def inject(self, app_path: str, paths: list):
        self.logger.info(f"Injecting dynamic libraries: {paths}")
        try:
            executable_path = self._get_executable_path(app_path)
            for path in paths:
                if path.endswith('.dylib'):
                    await self._inject_dylib(executable_path, path)
                elif path.endswith('.framework'):
                    await self._inject_framework(executable_path, path)
                else:
                    raise DylibInjectionError(f"Unsupported file type: {path}")
        except Exception as e:
            raise DylibInjectionError(f"Failed to inject dynamic library: {str(e)}")
    def _get_executable_path(self, app_path: str) -> str:
        plist_path = os.path.join(app_path, 'Info.plist')
        cmd = f"/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' {plist_path}"
        executable_name = subprocess.check_output(cmd, shell=True).decode().strip()
        return os.path.join(app_path, executable_name)

    async def _inject_framework(self, executable_path: str, framework_path: str):
        frameworks_dir = os.path.join(os.path.dirname(executable_path), 'Frameworks')
        if not os.path.exists(frameworks_dir):
            os.makedirs(frameworks_dir)
        
        destination_path = os.path.join(frameworks_dir, os.path.basename(framework_path))
        if os.path.exists(destination_path):
            os.remove(destination_path)
        
        shutil.copytree(framework_path, destination_path)

        optool_path = self.config.get_tool_path('optool')
        framework_name = os.path.basename(framework_path)
        cmd = f"{optool_path} install -c load -p '@executable_path/Frameworks/{framework_name}/{framework_name[:-10]}' -t {executable_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise DylibInjectionError(f"Injection failed for {framework_path}: {stderr.decode()}")
        self.logger.info(f"Successfully injected framework: {framework_name}")

    async def _inject_dylib(self, executable_path: str, dylib_path: str):
        dylib_name = os.path.basename(dylib_path)
        destination_path = os.path.join(os.path.dirname(executable_path), dylib_name)
        if os.path.exists(destination_path):
            os.remove(destination_path)
        shutil.copy(dylib_path, destination_path)
        
        optool_path = self.config.get_tool_path('optool')
        cmd = f"{optool_path} install -c load -p '@executable_path/{os.path.basename(dylib_path)}' -t {executable_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise DylibInjectionError(f"Injection failed for {dylib_name}: {stderr.decode()}")
        self.logger.info(f"Successfully injected dynamic library: {dylib_name}")