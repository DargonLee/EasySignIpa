import configparser


class EConfigHandler(object):
    def __init__(self, path):
        self.section_key = "DEFAULTCONFIG"
        self.identity_key = "codesign_identity_value"
        self.mobileprovision_path_key = "embedded_mobileprovision_path"

        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path, encoding="utf-8")

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

    def get_identity(self):
        return self.get(self.section_key, self.identity_key)

    def set_identity(self, identity):
        self.set(self.section_key, self.identity_key, identity)

    def get_mobileprovision_path(self):
        return self.get(self.section_key, self.mobileprovision_path_key)

    def set_mobileprovision_path(self, path):
        self.set(self.section_key, self.mobileprovision_path_key, path)


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
