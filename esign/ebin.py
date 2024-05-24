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
        print("[*] Install AppPath: {}".format(target_app_path))
        install_cmd = "{} -{} {} -W".format(
            IOS_DEPLOY_NEW_PATH, install_type, target_app_path
        )
        print(f"[*] {install_cmd}")
        install_cmd_result = subprocess.getoutput(install_cmd)
        print("[*] install_cmd result: {}".format(install_cmd_result))

    @staticmethod
    def codesign_app(target_app_path, entitlements_file, identity):
        print(Logger.green("✅ begin codesigning app"))
        print("[*] App Path: {}".format(target_app_path))
        print("[*] Entitlements Path: {}".format(entitlements_file))
        print("[*] Codesigning Identity: {}".format(identity))
        codesign_cmd = "codesign -f -s {} --no-strict --entitlements {} {}".format(
            identity, entitlements_file, target_app_path
        )
        codesign_cmd_result = subprocess.getoutput(codesign_cmd)
        print("[*] {}".format(codesign_cmd_result))

    @staticmethod
    def dump_app_entitlements(target_app_path, entitlements_file):
        print(Logger.blue("👉🏻 begin dump app entitlements"))
        print("[*] New EntitlementsPath: {}".format(entitlements_file))
        dump_app_cmd = "codesign -d --entitlements :- {} > {}".format(target_app_path, entitlements_file)
        dump_app_cmd_result = subprocess.getoutput(dump_app_cmd)
        print("[*] Dump app result {}".format(dump_app_cmd_result))

    @staticmethod
    def codesign_dylib(dylib_framework_path, identity):
        if not os.path.exists(dylib_framework_path):
            print(Logger.warning("⚠️ {} begin dump app entitlements".format(dylib_framework_path)))
        print("[*] Codesigning dylibs: {}".format(dylib_framework_path))
        codesign_cmd = "codesign -f -s {} {}".format(identity, dylib_framework_path)
        codesign_cmd_result = subprocess.getoutput(codesign_cmd)
        print("[*] Codesigning dylibs result: {}".format(codesign_cmd_result))

    @staticmethod
    def optool_inject(framework_name, execu_table_path):
        print(Logger.blue("👉🏻 begin optool inject"))
        optool_cmd = (
            '{} install -c load -p "@executable_path/Frameworks/{}" -t {}'.format(
                OPTOOL_PATH, framework_name, execu_table_path
            )
        )
        print("[*] Optool_cmd: {}".format(optool_cmd))
        optool_cmd_result = subprocess.getoutput(optool_cmd)
        return optool_cmd_result

    @staticmethod
    def optool_delete_unrestrict(execu_table_path):
        print(Logger.blue("👉🏻 begin delete unrestrict"))
        optool_cmd = (
            '{} unrestrict -t {}'.format(
                OPTOOL_PATH, execu_table_path
            )
        )
        print("[*] Optool cmd: {}".format(optool_cmd))
        optool_cmd_result = subprocess.getoutput(optool_cmd)
        print("[*] Optool cmd result: {}".format(optool_cmd_result))
        return optool_cmd_result

    @staticmethod
    def jtool2(param):
        print(Logger.blue("👉🏻 jtool2 {}".format(param)))
        jtool2_cmd = (
            '{} {}'.format(
                JTOOL2_PATH, param
            )
        )
        print(Logger.blue("👉🏻 Jtool2 cmd: {}").format(jtool2_cmd))
        jtool2_cmd_result = subprocess.getoutput(jtool2_cmd)
        print("[*] Jtool2 cmd result: {}".format(jtool2_cmd_result))
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
