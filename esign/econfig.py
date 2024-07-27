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
        self.mobileprovision_path_key = "embedded_mobileprovision_path"

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
        mobileprovision_path = self.get(self.section_key, self.mobileprovision_path_key)
        if not os.path.exists(mobileprovision_path):
            while True:
                mobileprovision_path = input(
                    Logger.green("Please provide the full path to the [debug] provisioning profile file: "))
                if os.path.exists(mobileprovision_path):
                    break
                else:
                    Logger.green("[debug] provisioning profile file path not exists")
            shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
            mobileprovision_name = os.path.basename(mobileprovision_path)
            mobileprovision_new_path = os.path.join(PROVISIONS_DIR_PATH, mobileprovision_name)
            self.set_debug_mobileprovision_path(mobileprovision_new_path)
            print(f'[*] SetEnv [debug] mobileprovision file success: {mobileprovision_new_path}')
            return mobileprovision_new_path
        else:
            return mobileprovision_path

    def set_debug_mobileprovision_path(self, path):
        self.set(self.section_key, self.mobileprovision_path_key, path)

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
            shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
            mobileprovision_name = os.path.basename(mobileprovision_path)
            mobileprovision_new_path = os.path.join(PROVISIONS_DIR_PATH, mobileprovision_name)
            self.set_release_mobileprovision_path(mobileprovision_new_path)
            print(f'[*] SetEnv [release] mobileprovision file success: {mobileprovision_new_path}')
            return mobileprovision_new_path
        else:
            return release_mobileprovision_path

    def set_release_mobileprovision_path(self, path):
        self.set(self.section_release_key, self.mobileprovision_path_release_key, path)


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
