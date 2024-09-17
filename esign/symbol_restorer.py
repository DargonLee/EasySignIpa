import asyncio
import os
from esign.elogger import Logger
from esign.econfig import ConfigHandler
from esign.exceptions import SymbolRestorationError

class SymbolRestorer:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def restore(self, executable_path: str):
        try:
            restore_symbol_path = self.config.get_tool_path('restore_symbol')
            if not os.path.exists(restore_symbol_path):
                raise SymbolRestorationError(f"restore-symbol 工具不存在: {restore_symbol_path}")

            self.logger.info(f"正在恢复符号表: {executable_path}")
            cmd = [restore_symbol_path, executable_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise SymbolRestorationError(f"恢复符号表失败: {stderr.decode()}")
            
            self.logger.info("符号表恢复成功")
        except Exception as e:
            raise SymbolRestorationError(f"恢复符号表过程中发生错误: {str(e)}")