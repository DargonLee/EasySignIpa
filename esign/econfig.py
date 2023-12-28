import configparser


class EConfigHandler(object):
    def __init__(self, path):
        self.section_key = "DEFAULTCONFIG"
        self.identity_key = "codesign_identity_value"
        self.mobileprovision_path_key = "embedded_mobileprovision_path"

        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def get(self, section, option):
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


def do_config():
    pass


if __name__ == "__main__":
    # 使用示例
    config_handler = EConfigHandler(
        "/Users/apple/Desktop/Github/EasySignIpa/config/settings.ini"
    )
    config_handler.set("DEFAULTss", "debug", "False")
    # 设置 DEFAULT section 下的 debug option 为 'False'
    # print(config_handler.get("DEFAULT_SECTION", "debug"))  # 读取 DEFAULT section 下的 debug option
