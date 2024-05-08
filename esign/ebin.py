import subprocess
import os
import platform
from esign.elogger import Logger
from esign.utils import IOS_DEPLOY_NEW_PATH, OPTOOL_PATH


def get_os():
    os_name = platform.system()
    if os_name == "Windows":
        return "Windows"
    elif os_name == "Darwin":
        return "Mac"
    else:
        return "Unknown"


class EBinTool(object):
    @staticmethod
    def install_app(target_app_path, IS_REINSTALL=False):
        print(Logger.green("✅ install app"))
        print("[-]AppPath => {}".format(target_app_path))
        install_type = "-b"
        if IS_REINSTALL:
            install_type = "-rb"
        install_cmd = "{} {} {} -W".format(
            IOS_DEPLOY_NEW_PATH, install_type, target_app_path
        )
        print(f"[-] {install_cmd}")
        os.system(install_cmd)

    @staticmethod
    def codesign_app(target_app_path, entitlements_file, identity):
        print(Logger.green("👉🏻 begin codesigning app"))
        print("[-]AppPath => {}".format(target_app_path))
        print("[-]CodesigningIdentity => {}".format(identity))
        codesign_cmd = "codesign -f -s {} --entitlements {} {}".format(
            identity, entitlements_file, target_app_path
        )
        codesign_cmd_result = subprocess.getoutput(codesign_cmd)
        print("{}".format(codesign_cmd_result))

    @staticmethod
    def codesign_dylib(dylib_framework_path, identity):
        if not os.path.exists(dylib_framework_path):
            print("{} => not exist".format(dylib_framework_path))
        print("[-]codesigning dylibs => {}".format(dylib_framework_path))
        codesign_cmd = "codesign -f -s {} {}".format(identity, dylib_framework_path)
        codesign_cmd_result = subprocess.getoutput(codesign_cmd)
        print("{}".format(codesign_cmd_result))

    @staticmethod
    def optool_inject(framework_name, execu_table_path):
        print(Logger.green("👉🏻 begin optool inject"))
        optool_cmd = (
            '{} install -c load -p "@executable_path/Frameworks/{}" -t {}'.format(
                OPTOOL_PATH, framework_name, execu_table_path
            )
        )
        print("[-]optool_cmd => {}".format(optool_cmd))
        optool_cmd_result = subprocess.getoutput(optool_cmd)
        return optool_cmd_result


if __name__ == "__main__":
    # EBinTool.optool_inject(
    #     "/Users/apple/Downloads/Payload/Vss.framework",
    #     " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    # )
    EBinTool.optool_inject(
        "/Users/apple/Downloads/Payload/libMacBox.dylib",
        " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    )