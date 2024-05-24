import subprocess
import os
import platform
from esign.elogger import Logger
from esign.utils import IOS_DEPLOY_NEW_PATH, OPTOOL_PATH, JTOOL2_PATH


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
    def install_app(target_app_path, install_type):
        print(Logger.green("✅ install app"))
        print("[-]Install AppPath => {}".format(target_app_path))
        install_cmd = "{} -{} {} -W".format(
            IOS_DEPLOY_NEW_PATH, install_type, target_app_path
        )
        print(f"[-] {install_cmd}")
        install_cmd_result = subprocess.getoutput(install_cmd)
        print("{}".format(install_cmd_result))

    @staticmethod
    def codesign_app(target_app_path, entitlements_file, identity):
        print(Logger.green("👉🏻 begin codesigning app"))
        print("[-]AppPath => {}".format(target_app_path))
        print("[-]EntitlementsPath => {}".format(entitlements_file))
        print("[-]CodesigningIdentity => {}".format(identity))
        codesign_cmd = "codesign -f -s {} --entitlements {} {}".format(
            identity, entitlements_file, target_app_path
        )
        codesign_cmd_result = subprocess.getoutput(codesign_cmd)
        print("{}".format(codesign_cmd_result))

    @staticmethod
    def dump_app_entitlements(target_app_path, entitlements_file):
        print(Logger.green("👉🏻 begin dump app entitlements"))
        print("[-]AppPath => {}".format(target_app_path))
        print("[-]New EntitlementsPath => {}".format(entitlements_file))
        dump_app_cmd = "codesign -d --entitlements :- {} > {}".format(target_app_path, entitlements_file)
        dump_app_cmd_result = subprocess.getoutput(dump_app_cmd)
        print("{}".format(dump_app_cmd_result))

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

    @staticmethod
    def optool_delete_unrestrict(execu_table_path):
        print(Logger.green("👉🏻 begin delete unrestrict"))
        optool_cmd = (
            '{} unrestrict -t {}'.format(
                OPTOOL_PATH, execu_table_path
            )
        )
        print("[-]optool_cmd => {}".format(optool_cmd))
        optool_cmd_result = subprocess.getoutput(optool_cmd)
        return optool_cmd_result

    @staticmethod
    def jtool2(param):
        print(Logger.green("✅ jtool2 {}".format(param)))
        jtool2_cmd = (
            '{} {}'.format(
                JTOOL2_PATH, param
            )
        )
        print("[-]jtool2_cmd => {}".format(jtool2_cmd))
        jtool2_cmd_result = subprocess.getoutput(jtool2_cmd)
        return jtool2_cmd_result


if __name__ == "__main__":
    # EBinTool.optool_inject(
    #     "/Users/apple/Downloads/Payload/Vss.framework",
    #     " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    # )
    EBinTool.optool_inject(
        "/Users/apple/Downloads/Payload/libMacBox.dylib",
        " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    )
