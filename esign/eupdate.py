from esign.econfig import EConfigHandler
from esign.utils import (
    SETTINGS_PATH
)


class EUpdate(object):
    def __init__(self):
        self.config = EConfigHandler(SETTINGS_PATH)

    @classmethod
    def update_mobileprovision(cls, src_path, model):
        instance = cls()
        src_path = src_path.strip()
        if not src_path.endswith('.mobileprovision'):
            raise ValueError(f"The source file {src_path} is not a .mobileprovision file")
        if model == "debug":
            instance.config.set_debug_mobileprovision_path(src_path)
        elif model == "release":
            instance.config.set_release_mobileprovision_path(src_path)
        else:
            raise Exception("update params error: {} , {}".format(src_path, model))

    @classmethod
    def update_identity(cls, identity_value, model):
        instance = cls()
        identity_value = identity_value.strip()
        if model == "debug":
            instance.config.set_debug_identity(identity_value)
        elif model == "release":
            instance.config.set_release_identity(identity_value)
        else:
            raise Exception("update params error: {} , {}".format(identity_value, model))

import os
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import ConfigError

class EUpdate:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    def update_mobileprovision(self, src_path: str, model: str):
        try:
            src_path = src_path.strip()
            if not src_path.endswith('.mobileprovision'):
                raise ConfigError(f"源文件 {src_path} 不是 .mobileprovision 文件")
            
            if not os.path.exists(src_path):
                raise ConfigError(f"文件不存在: {src_path}")

            if model == "debug":
                self.config.set_debug_mobileprovision_path(src_path)
            elif model == "release":
                self.config.set_release_mobileprovision_path(src_path)
            else:
                raise ConfigError(f"无效的更新模式: {model}")

            self.logger.info(f"成功更新 {model} 模式的 mobileprovision 文件")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"更新 mobileprovision 时发生未知错误: {str(e)}")

    def update_identity(self, identity_value: str, model: str):
        try:
            identity_value = identity_value.strip()
            if model == "debug":
                self.config.set_debug_identity(identity_value)
            elif model == "release":
                self.config.set_release_identity(identity_value)
            else:
                raise ConfigError(f"无效的更新模式: {model}")

            self.logger.info(f"成功更新 {model} 模式的签名身份")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"更新签名身份时发生未知错误: {str(e)}")

    def update_tool_path(self, tool_name: str, tool_path: str):
        try:
            tool_path = tool_path.strip()
            if not os.path.exists(tool_path):
                raise ConfigError(f"工具路径不存在: {tool_path}")

            self.config.set(tool_name, tool_path, 'TOOLS')
            self.logger.info(f"成功更新工具 {tool_name} 的路径")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"更新工具路径时发生未知错误: {str(e)}")

    def list_config(self):
        try:
            all_config = self.config.get_all()
            self.logger.info("当前配置:")
            for section, options in all_config.items():
                self.logger.info(f"[{section}]")
                for key, value in options.items():
                    self.logger.info(f"  {key} = {value}")
        except Exception as e:
            self.logger.error(f"列出配置时发生错误: {str(e)}")