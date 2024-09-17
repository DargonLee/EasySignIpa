import configparser
import os
import shutil
import subprocess
from esign.elogger import Logger
from esign.utils import (
    PROVISIONS_DIR_PATH
)


class EConfigHandler(object):
    def __init__(self, path):
        self.section_key = "DEFAULTCONFIG"
        self.identity_key = "codesign_identity_value"
        self.mobileprovision_path_debug_key = "embedded_mobileprovision_path"

        self.section_release_key = "RDEFAULTCONFIG"
        self.identity_release_key = "codesign_identity_value_release"
        self.mobileprovision_path_release_key = "embedded_mobileprovision_path_release"

        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path, encoding="utf-8")

    ### core
    def get(self, section, option):
        if section not in self.config.sections():
            return None
        if option not in self.config.options(section):
            return None
        return self.config.get(section, option)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

        with open(self.path, "w") as configfile:
            self.config.write(configfile)

    ### debug
    def get_debug_identity(self):
        debug_identity = self.get(self.section_key, self.identity_key)
        if not debug_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(Logger.green("Please select the [debug] identity value for the certificate: "))
            self.set_debug_identity(identity)
            print('[*] SetEnv [debug] identity: {} success'.format(identity))
            return identity
        else:
            return debug_identity

    def set_debug_identity(self, identity):
        self.set(self.section_key, self.identity_key, identity)

    def get_debug_mobileprovision_path(self):
        mobileprovision_path = self.get(self.section_key, self.mobileprovision_path_debug_key)
        if not os.path.exists(mobileprovision_path):
            while True:
                mobileprovision_path = input(
                    Logger.green("Please provide the full path to the [debug] provisioning profile file: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    Logger.green("[debug] provisioning profile file path not exists")
            return self.set_debug_mobileprovision_path(mobileprovision_path)
        else:
            return mobileprovision_path

    def set_debug_mobileprovision_path(self, mobileprovision_path):
        shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(PROVISIONS_DIR_PATH, mobileprovision_name)
        self.set(self.section_key, self.mobileprovision_path_debug_key, mobileprovision_new_path)
        print(f'[*] SetEnv [debug] mobileprovision file success: {mobileprovision_new_path}')
        return mobileprovision_new_path

    ### release
    def get_release_identity(self):
        release_identity = self.get(self.section_release_key, self.identity_release_key)
        if not release_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(Logger.green("Please select the [release] identity value for the certificate: "))
            self.set_release_identity(identity)
            print('[*] SetEnv [release] identity: {} success'.format(identity))
            return identity
        else:
            return release_identity

    def set_release_identity(self, identity):
        self.set(self.section_release_key, self.identity_release_key, identity)

    def get_release_mobileprovision_path(self):
        release_mobileprovision_path = self.get(self.section_release_key, self.mobileprovision_path_release_key)
        if not os.path.exists(release_mobileprovision_path):
            while True:
                mobileprovision_path = input(
                    Logger.green("Please provide the full path to the [release] provisioning profile file: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    Logger.red("[release] provisioning profile file path not exists")
            return self.set_release_mobileprovision_path(mobileprovision_path)
        else:
            return release_mobileprovision_path

    def set_release_mobileprovision_path(self, mobileprovision_path):
        shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(PROVISIONS_DIR_PATH, mobileprovision_name)
        self.set(self.section_release_key, self.mobileprovision_path_release_key, mobileprovision_new_path)
        print(f'[*] SetEnv [release] mobileprovision file success: {mobileprovision_new_path}')
        return mobileprovision_new_path


import configparser
import os
import shutil
import subprocess
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
                self.logger.warning(f"配置文件不存在: {self.config_file_path}")
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {str(e)}")

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
                'temp_dir': '/tmp/esign',
            },
            'TOOLS': {
                'ios_deploy': os.path.expanduser("~/.esign/bin/ios-deploy"),
                'optool': os.path.expanduser("~/.esign/bin/optool"),
                'jtool2': os.path.expanduser("~/.esign/bin/jtool2"),
                'restore_symbol': os.path.expanduser("~/.esign/bin/restore-symbol"),
            }
        }

        for section, options in defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, str(value))

        self._save_config()

    def _save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w', encoding="utf-8") as configfile:
                self.config.write(configfile)
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {str(e)}")

    def get(self, key: str, section: str = 'GENERAL') -> str:
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise ConfigError(f"配置项不存在: [{section}] {key}")

    def set(self, key: str, value: str, section: str = 'GENERAL'):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self._save_config()

    def get_debug_identity(self) -> str:
        debug_identity = self.get('codesign_identity_value', 'DEFAULTCONFIG')
        if not debug_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(self.logger.green("请选择 [debug] 证书的身份值: "))
            self.set_debug_identity(identity)
            self.logger.info(f'[*] 设置 [debug] 身份: {identity} 成功')
            return identity
        return debug_identity

    def set_debug_identity(self, identity: str):
        self.set('codesign_identity_value', identity, 'DEFAULTCONFIG')

    def get_release_identity(self) -> str:
        release_identity = self.get('codesign_identity_value_release', 'RDEFAULTCONFIG')
        if not release_identity:
            subprocess.call("security find-identity -v -p codesigning", shell=True)
            identity = input(self.logger.green("请选择 [release] 证书的身份值: "))
            self.set_release_identity(identity)
            self.logger.info(f'[*] 设置 [release] 身份: {identity} 成功')
            return identity
        return release_identity

    def set_release_identity(self, identity: str):
        self.set('codesign_identity_value_release', identity, 'RDEFAULTCONFIG')

    def get_debug_mobileprovision_path(self) -> str:
        mobileprovision_path = self.get('embedded_mobileprovision_path', 'DEFAULTCONFIG')
        if not os.path.exists(mobileprovision_path):
            while True:
                mobileprovision_path = input(self.logger.green("请提供 [debug] 配置文件的完整路径: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    self.logger.warning("[debug] 配置文件路径不存在")
            return self.set_debug_mobileprovision_path(mobileprovision_path)
        return mobileprovision_path

    def set_debug_mobileprovision_path(self, mobileprovision_path: str) -> str:
        os.makedirs(self.provisions_dir_path, exist_ok=True)
        shutil.copy(mobileprovision_path, self.provisions_dir_path)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(self.provisions_dir_path, mobileprovision_name)
        self.set('embedded_mobileprovision_path', mobileprovision_new_path, 'DEFAULTCONFIG')
        self.logger.info(f'[*] 设置 [debug] 配置文件成功: {mobileprovision_new_path}')
        return mobileprovision_new_path

    def get_release_mobileprovision_path(self) -> str:
        release_mobileprovision_path = self.get('embedded_mobileprovision_path_release', 'RDEFAULTCONFIG')
        if not os.path.exists(release_mobileprovision_path):
            while True:
                mobileprovision_path = input(self.logger.green("请提供 [release] 配置文件的完整路径: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    self.logger.warning("[release] 配置文件路径不存在")
            return self.set_release_mobileprovision_path(mobileprovision_path)
        return release_mobileprovision_path

    def set_release_mobileprovision_path(self, mobileprovision_path: str) -> str:
        os.makedirs(self.provisions_dir_path, exist_ok=True)
        shutil.copy(mobileprovision_path, self.provisions_dir_path)
        mobileprovision_name = os.path.basename(mobileprovision_path)
        mobileprovision_new_path = os.path.join(self.provisions_dir_path, mobileprovision_name)
        self.set('embedded_mobileprovision_path_release', mobileprovision_new_path, 'RDEFAULTCONFIG')
        self.logger.info(f'[*] 设置 [release] 配置文件成功: {mobileprovision_new_path}')
        return mobileprovision_new_path

    def get_tool_path(self, tool_name: str) -> str:
        return self.get(tool_name, 'TOOLS')

    def validate(self) -> bool:
        required_tools = ['ios_deploy', 'optool', 'jtool2', 'restore_symbol']
        for tool in required_tools:
            tool_path = self.get_tool_path(tool)
            if not os.path.exists(tool_path):
                self.logger.error(f"工具不存在: {tool} ({tool_path})")
                return False
        return True

    def get_all(self) -> Dict[str, Dict[str, str]]:
        return {section: dict(self.config[section]) for section in self.config.sections()}


if __name__ == "__main__":
    # 使用示例
    config_handler = EConfigHandler(
        "/Users/apple/Desktop/Github/EasySignIpa/config/settings.ini"
    )
    print(config_handler.config.sections())
    print(config_handler.get_debug_mobileprovision_path())
    config_handler.get("DEFAULT_SECTION", "debug")  # 读取 DEFAULT section 下的 debug option
    # config_handler.set("DEFAULTss", "debug", "False")
    # 设置 DEFAULT section 下的 debug option 为 'False'
    # print(config_handler.get("DEFAULT_SECTION", "debug"))  # 读取 DEFAULT section 下的 debug option
