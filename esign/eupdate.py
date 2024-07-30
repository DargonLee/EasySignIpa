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
