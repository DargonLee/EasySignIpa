import asyncio
import os
from esign.elogger import Logger
from esign.econfig import ConfigHandler
from esign.exceptions import SymbolRestorationError

class SymbolRestorer:

    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def restore(self, executable_path: str, plugin_path: str = None):
        try:
            if executable_path:
                await self._restore_symbol(executable_path)

            plugin_path = os.path.join(os.path.dirname(executable_path), 'PlugIns')
            if os.path.exists(plugin_path):
                await self._restore_plugin(plugin_path)

        except Exception as e:
            raise SymbolRestorationError(f"An error occurred during symbol table restoration: {str(e)}")

    async def _restore_plugin(self, plugin_path: str):
        self.logger.info(f"Starting symbol table restoration in plugin directory: {plugin_path}")

        tasks = []

        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                # 假设插件中的可执行文件是没有扩展名的文件，或者你可以根据实际需要调整匹配规则
                if not file.endswith('.dylib') and not file.endswith('.framework'):
                    executable_path = os.path.join(root, file)
                    tasks.append(self._restore_symbol_with_logging(executable_path))

        if tasks:
            await asyncio.gather(*tasks)

        self.logger.info("Symbol table restoration in plugin directory completed")

    async def _restore_symbol_with_logging(self, executable_path: str):
            # 恢复插件中的可执行文件符号表
            self.logger.info(f"Restoring symbol table in plugin: {executable_path}")
            try:
                await self._restore_symbol(executable_path)
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while restoring plugin {executable_path}: {str(e)}")

    async def _restore_symbol(self, executable_path: str):
        restore_symbol_path = self.config.get_tool_path('restore_symbol')
        if not os.path.exists(restore_symbol_path):
            raise SymbolRestorationError(f"restore-symbol tool does not exist: {restore_symbol_path}")

        self.logger.info(f"Restoring symbol table for app: {executable_path}")
        tmp_path = '{}_1'.format(executable_path)
        cmd = [restore_symbol_path, executable_path, '-o', tmp_path]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise SymbolRestorationError(f"Failed to restore symbol table: {stderr.decode()}")

        executable_name = os.path.basename(executable_path)
        if "Finish" not in stdout.decode():
            self.logger.error(f"Symbol table restoration failed for {executable_name}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False
        
        os.remove(executable_path)
        os.rename(tmp_path, executable_path)
        self.logger.info(f"Symbol table restoration successful for {executable_name}")
        return True