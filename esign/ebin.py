import plistlib
import struct
import subprocess
import os
import shlex
import platform
from esign.elogger import Logger
from esign.utils import (
    IOS_DEPLOY_NEW_PATH,
    OPTOOL_PATH,
    JTOOL2_PATH,
    RESTORE_SYMBOL_PATH
)


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
    def run_sub_command(cmd_line):
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

    @staticmethod
    def install_app(target_app_path, install_type, device_id):
        print(Logger.green("✅ install app"))
        print("[*] Install AppPath: {}".format(target_app_path))
        if device_id:
            install_cmd = "{} -{} {} -i {} -W".format(
                IOS_DEPLOY_NEW_PATH, install_type,target_app_path,device_id
            )
        else:
            install_cmd = "{} -{} {} -W".format(
                IOS_DEPLOY_NEW_PATH, install_type, target_app_path
            )
        print(f"[*] {install_cmd}")
        # install_cmd_result = subprocess.getoutput(install_cmd)
        return_code = EBinTool.run_sub_command(install_cmd)
        print("[Done] install_cmd done with result code {}".format(return_code))

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

        is_dump_success = True
        if "an invalid entitlements" in dump_app_cmd_result:
            os.remove(entitlements_file)
            is_dump_success = False

        if not is_dump_success:
            print(Logger.blue("[*] Use Jtool2 Dump app entitlements"))
            app_name_with_extension = os.path.basename(target_app_path)
            app_name = os.path.splitext(app_name_with_extension)[0]
            new_target_app_path = os.path.join(target_app_path, app_name)
            jtool2_cmd = "{} --ent {} > {}".format(
                JTOOL2_PATH, new_target_app_path, entitlements_file
            )
            print(f"[*] jtool2 cmd: {jtool2_cmd}")
            jtool2_cmd_result = subprocess.getoutput(jtool2_cmd)
            print("[*] jtool2_cmd result: {}".format(jtool2_cmd_result))
        print("[*] Dump app result {}".format(dump_app_cmd_result))
        try:
            if os.path.exists(entitlements_file):
                with open(entitlements_file, 'rb') as f:
                    plist_data = plistlib.load(f)
                    if len(plist_data) > 0:
                        print("[*] Dump app entitlements success")
        except Exception as e:
            print(f"[!] Failed to dump app entitlements: {e}")

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
    def jtool2(params):
        print(Logger.blue("👉🏻 jtool2 {}".format(params)))
        jtool2_cmd = (
            '{} {}'.format(
                JTOOL2_PATH, params
            )
        )
        print(Logger.blue("👉🏻 Jtool2 cmd: {}").format(jtool2_cmd))
        jtool2_cmd_result = subprocess.getoutput(jtool2_cmd)
        print("[*] Jtool2 cmd result: {}".format(jtool2_cmd_result))
        return jtool2_cmd_result

    @staticmethod
    def restore_symbol(params):
        """
        restore-symbol CJTest -o CJTest_symbol
        """
        file_re = os.path.basename(params)
        print(Logger.blue("👉🏻 restore_symbol {}".format(file_re)))
        tmp_path = '{}_1'.format(params)
        restore_symbol_cmd = (
            '{} {} -o {}'.format(
                RESTORE_SYMBOL_PATH, params, tmp_path
            )
        )
        print(Logger.blue("👉🏻 restore_symbol cmd: {}").format(restore_symbol_cmd))
        restore_symbol_cmd_result = subprocess.getoutput(restore_symbol_cmd)
        if "Finish" in restore_symbol_cmd_result:
            os.remove(params)
            os.rename(tmp_path, params)
            print("[*] {} restore_symbol success".format(file_re))
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print("[*] {} restore_symbol fail: {}".format(file_re, restore_symbol_cmd_result))
        return restore_symbol_cmd_result

    @staticmethod
    def atos(params):
        """
        atos -arch arm64 -o CJTest_arm64_symbol -l 0x1045e8000 0x0000000105b8b738 0x0000000105b8b724
        """
        print(Logger.blue("👉🏻 atos cmd: {}".format(params)))
        atos_cmd = (
            'atos -arch arm64 {}'.format(params)
        )
        print(Logger.blue("👉🏻 atos cmd: {}").format(atos_cmd))
        atos_cmd_result = subprocess.getoutput(atos_cmd)
        print("[*] atos cmd result: {}".format(atos_cmd_result))
        return atos_cmd_result

    @staticmethod
    def otool(params):
        """
        otool
        """
        otool_cmd = (
            'otool {}'.format(params)
        )
        print(Logger.blue("👉🏻 otool cmd: {}").format(otool_cmd))
        otool_cmd_result = subprocess.getoutput(otool_cmd)
        print("[*] otool cmd result: {}".format(otool_cmd_result))
        return otool_cmd_result

    @staticmethod
    def otool_macho_cryptid(macho_path):
        """
        otool -l WeChart | grep cryptid
        """
        otool_cmd = (
            '-l {} | grep cryptid'.format(macho_path)
        )
        otool_cmd_result = EBinTool.otool(otool_cmd)
        is_crypt = True
        if "cryptid 0" in otool_cmd_result:
            is_crypt = False
        return is_crypt
    
    @staticmethod
    def is_encrypted_by_otool(executable_path):
        """
        检查可执行文件是否加密
        
        参数:
        executable_path: 可执行文件的路径
        
        返回:
        bool: 如果文件加密返回True,否则返回False
        """
        print(Logger.blue(f"👉🏻 检查文件是否加密: {executable_path}"))
        
        otool_cmd = f"-l {executable_path} | grep cryptid"
        otool_result = EBinTool.otool(otool_cmd)
        
        if "cryptid 1" in otool_result:
            print(Logger.yellow(f"⚠️ 文件已加密: {executable_path}"))
            return True
        elif "cryptid 0" in otool_result:
            print(Logger.green(f"✅ 文件未加密: {executable_path}"))
            return False
        else:
            print(Logger.error(f"错误: 无法确定文件加密状态: {executable_path}"))
            return False
        
    @staticmethod
    def is_encrypted_by_macho(file_path):
        """
        检测 iOS 可执行文件是否加密

        参数:
        file_path (str): 可执行文件的路径

        返回:
        bool: 如果文件加密返回 True，否则返回 False
        """
        try:
            if not os.path.exists(file_path):
                print(f"错误: 文件不存在 - {file_path}")
                return None

            with open(file_path, 'rb') as f:
                # 读取 Mach-O 头部
                magic = struct.unpack('<I', f.read(4))[0]
                
                # 检查是否为有效的 Mach-O 文件
                if magic not in (0xfeedface, 0xfeedfacf, 0xcefaedfe, 0xcffaedfe):
                    print(f"错误: 不是有效的 Mach-O 文件 - {file_path}")
                    return None

                # 定位到 LC_ENCRYPTION_INFO 或 LC_ENCRYPTION_INFO_64 加载命令
                f.seek(28 if magic in (0xfeedface, 0xcefaedfe) else 32)  # 跳过头部
                ncmds = struct.unpack('<I', f.read(4))[0]  # 加载命令数量

                for _ in range(ncmds):
                    cmd, cmdsize = struct.unpack('<II', f.read(8))
                    if cmd in (0x21, 0x2C):  # LC_ENCRYPTION_INFO 或 LC_ENCRYPTION_INFO_64
                        f.seek(8, 1)  # 跳过 offset 和 size
                        cryptid = struct.unpack('<I', f.read(4))[0]
                        
                        if cryptid == 1:
                            print(f"文件已加密: {file_path}")
                            return True
                        elif cryptid == 0:
                            print(f"文件未加密: {file_path}")
                            return False
                    else:
                        f.seek(cmdsize - 8, 1)  # 跳到下一个加载命令

                print(f"未找到加密信息: {file_path}")
                return False

        except Exception as e:
            print(f"分析过程中发生错误: {str(e)}")
            return None


if __name__ == "__main__":
    # EBinTool.optool_inject(
    #     "/Users/apple/Downloads/Payload/Vss.framework",
    #     " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    # )
    # EBinTool.optool_inject(
    #     "/Users/apple/Downloads/Payload/libMacBox.dylib",
    #     " /Users/apple/Downloads/Payload/sacurity.app/sacurity",
    # )
    # EBinTool.install_app("/Users/apple/Downloads/Payload/Lark.app", "b")
    EBinTool.otool_macho_cryptid("/Users/apple/Downloads/Payload/WeChat.app/WeChat")
