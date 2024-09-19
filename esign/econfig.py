import configparser
import os
import shutil
import subprocess
from shlex import shlex
from typing import Any, Dict
from esign.exceptions import ConfigError
from esign.elogger import Logger

class ConfigHandler:
    def __init__(self, config_file_path: str = None):
        self.logger = Logger()
        self.config_file_path = config_file_path or os.path.expanduser("~/.esign/config.ini")
        self.provisions_dir_path = os.path.expanduser("~/.esign/provisions")
        self.config = configparser.ConfigParser()
        self._load_config()
        self._set_defaults()

    def _load_config(self):
        try:
            if os.path.exists(self.config_file_path):
                self.config.read(self.config_file_path, encoding="utf-8")
            else:
                self.logger.warning(f"Configuration file does not exist: {self.config_file_path}")
        except Exception as e:
            raise ConfigError(f"Failed to load configuration file: {str(e)}")
    def _set_defaults(self):
        defaults = {
            'DEFAULTCONFIG': {
                'codesign_identity_value': '',
                'embedded_mobileprovision_path': '',
            },
            'RDEFAULTCONFIG': {
                'codesign_identity_value_release': '',
                'embedded_mobileprovision_path_release': '',
            },
            'GENERAL': {
                'esign_dir': os.path.expanduser("~/.esign"),
                'provisions_dir': self.provisions_dir_path,
            },
            'TOOLS': {
                'ios-deploy_new': os.path.expanduser("~/.esign/bin/ios-deploy_new"),
                'optool': os.path.expanduser("~/.esign/bin/optool"),
                'jtool2': os.path.expanduser("~/.esign/bin/jtool2"),
                'restore_symbol': os.path.expanduser("~/.esign/bin/restore-symbol"),
                'ideviceinstaller': os.path.expanduser("~/.esign/bin/ideviceinstaller"),
                'unsign': os.path.expanduser("~/.esign/bin/unsign")
            }
        }

        for section, options in defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, str(value))

        self._save_config()

    def run_sub_command(self, cmd_line):
        args = shlex.split(cmd_line)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            output = process.stdout.readline().rstrip()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc

    def _save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w', encoding="utf-8") as configfile:
                self.config.write(configfile)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration file: {str(e)}")

    def get(self, key: str, section: str = 'GENERAL') -> str:
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise ConfigError(f"Configuration item does not exist: [{section}] {key}")

    def set(self, key: str, value: str, section: str = 'GENERAL'):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self._save_config()

    def get_debug_identity(self) -> str:
        debug_identity = self.get('codesign_identity_value', 'DEFAULTCONFIG')
        if not debug_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(self.logger.green("Please enter the identity value for the [debug] certificate: "))
            self.set_debug_identity(identity)
            self.logger.info(f'Successfully set [debug] identity to: {identity}')
            return identity
        return debug_identity

    def set_debug_identity(self, identity: str):
        self.set('codesign_identity_value', identity, 'DEFAULTCONFIG')

    def get_release_identity(self) -> str:
        release_identity = self.get('codesign_identity_value_release', 'RDEFAULTCONFIG')
        if not release_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(self.logger.green("Please enter the identity value for the [release] certificate: "))
            self.set_release_identity(identity)
            self.logger.info(f'[*] Successfully set [release] identity to: {identity}')
            return identity
        return release_identity

    def set_release_identity(self, identity: str):
        self.set('codesign_identity_value_release', identity, 'RDEFAULTCONFIG')

    def get_debug_mobileprovision_path(self) -> str:
        mobileprovision_path = self.get('embedded_mobileprovision_path', 'DEFAULTCONFIG')
        if not os.path.exists(mobileprovision_path):
            while True:
                mobileprovision_path = input(self.logger.green("Please provide the full path to the [debug] provisioning profile: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    self.logger.warning("[debug] Provisioning profile path does not exist")
            return self.set_debug_mobileprovision_path(mobileprovision_path)
        return mobileprovision_path

    def set_debug_mobileprovision_path(self, mobileprovision_path: str) -> str:
        os.makedirs(self.provisions_dir_path, exist_ok=True)
        shutil.copy(mobileprovision_path, self.provisions_dir_path)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(self.provisions_dir_path, mobileprovision_name)
        self.set('embedded_mobileprovision_path', mobileprovision_new_path, 'DEFAULTCONFIG')
        self.logger.info(f'[*] Successfully set [debug] provisioning profile: {mobileprovision_new_path}')
        return mobileprovision_new_path

    def get_release_mobileprovision_path(self) -> str:
        release_mobileprovision_path = self.get('embedded_mobileprovision_path_release', 'RDEFAULTCONFIG')
        if not os.path.exists(release_mobileprovision_path):
            while True:
                mobileprovision_path = input(
                    self.logger.info("Please provide the full path to the [release] provisioning profile: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    self.logger.warning("[release] Provisioning profile path does not exist")
            return self.set_release_mobileprovision_path(mobileprovision_path)
        return release_mobileprovision_path

    def set_release_mobileprovision_path(self, mobileprovision_path: str) -> str:
        os.makedirs(self.provisions_dir_path, exist_ok=True)
        shutil.copy(mobileprovision_path, self.provisions_dir_path)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(self.provisions_dir_path, mobileprovision_name)
        self.set('embedded_mobileprovision_path_release', mobileprovision_new_path, 'RDEFAULTCONFIG')
        self.logger.info(f'[*] Successfully set [release] provisioning profile: {mobileprovision_new_path}')
        return mobileprovision_new_path

    def get_tool_path(self, tool_name: str) -> str:
        return self.get(tool_name, 'TOOLS')

    def validate(self) -> bool:
        required_tools = ['ios-deploy_new', 'optool', 'jtool2', 'restore_symbol']
        for tool in required_tools:
            tool_path = self.get_tool_path(tool)
            if not os.path.exists(tool_path):
                self.logger.error(f"Tool does not exist: {tool} ({tool_path})")
                return False
        return True

    def get_all(self) -> Dict[str, Dict[str, str]]:
        return {section: dict(self.config[section]) for section in self.config.sections()}

if __name__ == "__main__":
    # 使用示例
    config_handler = ConfigHandler(
        "/Users/apple/Desktop/Github/EasySignIpa/config/settings.ini"
    )
    print(config_handler.config.sections())
    print(config_handler.get_debug_mobileprovision_path())
    config_handler.get("DEFAULT_SECTION", "debug")  # 读取 DEFAULT section 下的 debug option
    # config_handler.set("DEFAULTss", "debug", "False")
    # 设置 DEFAULT section 下的 debug option 为 'False'
    # print(config_handler.get("DEFAULT_SECTION", "debug"))  # 读取 DEFAULT section 下的 debug option
