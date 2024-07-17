import configparser
import os

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
    def get_identity(self):
        return self.get(self.section_key, self.identity_key)

    def set_identity(self, identity):
        self.set(self.section_key, self.identity_key, identity)

    def get_mobileprovision_path(self):
        mobileprovision_path = self.get(self.section_key, self.mobileprovision_path_key)
        return False
        if not os.path.exists(mobileprovision_path):
            raise False
        else:
            return True
    def set_mobileprovision_path(self, path):
        self.set(self.section_key, self.mobileprovision_path_key, path)

    ### release
    def get_release_identity(self):
        return self.get(self.section_release_key, self.identity_release_key)

    def set_release_identity(self, identity):
        self.set(self.section_release_key, self.identity_release_key, identity)

    def get_release_mobileprovision_path(self):
        release_mobileprovision_path = self.get(self.section_release_key, self.mobileprovision_path_release_key)
        if not os.path.exists(release_mobileprovision_path):
            raise False
        else:
            return True

    def set_release_mobileprovision_path(self, path):
        self.set(self.section_release_key, self.mobileprovision_path_release_key, path)


if __name__ == "__main__":
    # 使用示例
    config_handler = EConfigHandler(
        "/Users/apple/Desktop/Github/EasySignIpa/config/settings.ini"
    )
    print(config_handler.config.sections())
    print(config_handler.get_mobileprovision_path())
    config_handler.get("DEFAULT_SECTION", "debug")  # 读取 DEFAULT section 下的 debug option
    # config_handler.set("DEFAULTss", "debug", "False")
    # 设置 DEFAULT section 下的 debug option 为 'False'
    # print(config_handler.get("DEFAULT_SECTION", "debug"))  # 读取 DEFAULT section 下的 debug option
