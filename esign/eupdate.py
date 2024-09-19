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
                raise ConfigError(f"Source file {src_path} is not a .mobileprovision file")

            if not os.path.exists(src_path):
                raise ConfigError(f"File does not exist: {src_path}")

            if model == "debug":
                self.config.set_debug_mobileprovision_path(src_path)
            elif model == "release":
                self.config.set_release_mobileprovision_path(src_path)
            else:
                raise ConfigError(f"Invalid update mode: {model}")

            self.logger.info(f"Successfully updated mobileprovision file in {model} mode")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"An unknown error occurred while updating mobileprovision: {str(e)}")

    def update_identity(self, identity_value: str, model: str):
        try:
            identity_value = identity_value.strip()
            if model == "debug":
                self.config.set_debug_identity(identity_value)
            elif model == "release":
                self.config.set_release_identity(identity_value)
            else:
                raise ConfigError(f"Invalid update mode: {model}")

            self.logger.info(f"Successfully updated signing identity in {model} mode")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"An unknown error occurred while updating signing identity: {str(e)}")

    def update_tool_path(self, tool_name: str, tool_path: str):
        try:
            tool_path = tool_path.strip()
            if not os.path.exists(tool_path):
                raise ConfigError(f"Tool path does not exist: {tool_path}")

            self.config.set(tool_name, tool_path, 'TOOLS')
            self.logger.info(f"Successfully updated path for tool {tool_name}")
        except ConfigError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(f"An unknown error occurred while updating tool path: {str(e)}")

    def list_config(self):
        try:
            all_config = self.config.get_all()
            self.logger.error(f"An unknown error occurred while updating tool path: {str(e)}")
            for section, options in all_config.items():
                self.logger.info(f"[{section}]")
                for key, value in options.items():
                    self.logger.info(f"  {key} = {value}")
        except Exception as e:
            self.logger.error(f"get config all error: {str(e)}")