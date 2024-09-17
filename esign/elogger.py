class Logger:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    CYAN = "\033[36m"
    END = "\033[0m"

    def __init__(self):
        print("init tool")

    @staticmethod
    def cyan(msg):
        return Logger.CYAN + msg + Logger.END

    @staticmethod
    def blue(msg):
        return Logger.BLUE + msg + Logger.END

    @staticmethod
    def white(msg):
        return Logger.WHITE + msg + Logger.END

    @staticmethod
    def red(msg):
        return Logger.RED + msg + Logger.END

    @staticmethod
    def green(msg):
        return Logger.GREEN + msg + Logger.END

    @staticmethod
    def yellow(msg):
        return Logger.YELLOW + msg + Logger.END

    @staticmethod
    def info(msg):
        print(Logger.WHITE + msg + Logger.END)

    @staticmethod
    def warning(msg):
        print(Logger.YELLOW + msg + Logger.END)

    @staticmethod
    def error(msg):
        print(Logger.RED + msg + Logger.END)

import logging
import os
from datetime import datetime
from typing import Optional

class ColorFormatter(logging.Formatter):
    """自定义的日志格式化器，支持颜色输出"""

    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',   # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[95m',  # 紫色
        'RESET': '\033[0m'  # 重置颜色
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{log_message}{self.COLORS['RESET']}"

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        self.logger = logging.getLogger('ESign')
        self.logger.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    @staticmethod
    def cyan(msg: str) -> str:
        return f"\033[36m{msg}\033[0m"

    @staticmethod
    def blue(msg: str) -> str:
        return f"\033[94m{msg}\033[0m"

    @staticmethod
    def green(msg: str) -> str:
        return f"\033[92m{msg}\033[0m"

    @staticmethod
    def yellow(msg: str) -> str:
        return f"\033[93m{msg}\033[0m"

    @staticmethod
    def red(msg: str) -> str:
        return f"\033[91m{msg}\033[0m"

    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
        else:
            self.warning(f"Invalid log level: {level}. Using default (INFO).")

    def add_file_handler(self, file_path: str, level: Optional[str] = 'DEBUG'):
        """添加额外的文件处理器"""
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(getattr(logging, level))
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

if __name__ == "__main__":
    print(Logger.red("I am red! {}".format(["Lee", "Lee1"])))
    print(Logger.green("I am green!"))
    print(Logger.yellow("I am yellow!"))
    print(Logger.blue("I am blue!"))
    print(Logger.cyan("I am cyan!"))
    print(Logger.white("I am white!"))
