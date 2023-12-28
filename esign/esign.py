import os
import shutil
import subprocess
from ezip import EZipFile
from elogger import Logger
from econfig import EConfigHandler
from ebin import EBinTool
from utils import (
    SETTINGS_PATH,
    PROVISIONS_DIR_PATH,
    ESIGN_DIR_PATH,
    PROFILE_PLIST,
    EMBEDDED_ENTITLEMENTS,
)


class ESign(object):
    def __init__(self, app_path, dylibs=[], is_output_ipa=False, install_type=None):
        self.target_app_path = app_path
        self.inject_dylibs = dylibs
        self.output_ipa = is_output_ipa
        self.install_type = install_type
        self.payload_path = ""
        self.app_name = ""
        self.mobileprovision_path = ""

        self.target_app_path = "/Users/apple/Downloads/sacurity-4.3.5-1-prejg.ipa"
        # self.target_app_path = "/Users/apple/Downloads/Payload/sacurity.app"

    def check_run_env(self):
        config = EConfigHandler(SETTINGS_PATH)

        sign_identity = config.get_identity()
        if not sign_identity:
            self._execute_shell("security find-identity -v -p codesigning")
            sign_identity = input("请输入证书identity值:")
            config.set_identity(sign_identity)
            self.identity = sign_identity
            return False

        embedded_path = config.get_mobileprovision_path()
        if not embedded_path:
            embedded_path = input("请输入描述文件路径:")
            shutil.copy(embedded_path, PROVISIONS_DIR_PATH)
            name, exten = os.path.splitext(embedded_path)
            self.mobileprovision_path = os.path.join(PROVISIONS_DIR_PATH, exten)
            config.set_mobileprovision_path(self.mobileprovision_path)

        return True

    def prepare_app_path(self):
        self.current_path = os.getcwd()
        print(f"current_path => {self.current_path}")
        if os.path.isabs(self.target_app_path):
            self.target_app_path = os.path.dirname(self.target_app_path)

        app_name, extension = os.path.splitext(self.target_app_path)
        app_extension = extension[1:]
        self.app_name = app_name

        if (
            not os.path.isfile(self.target_app_path)
            or extension != ".ipa"
            or extension != ".app"
        ):
            print(f"Error: {self.target_app_path} does not exist.")
            exit(1)

        if app_extension == "ipa":
            import tempfile

            tempdir = tempfile.mkdtemp()
            EZipFile.unzip_file(self.target_app_path, tempdir)
            payload_path = os.path.join(tempdir, "Payload")
            self.payload_path = payload_path
            self.app_name = os.listdir(payload_path)[0]
            self.target_app_path = os.path.join(payload_path, self.app_name)
        else:
            self.payload_path = os.path.dirname(self.target_app_path)

        print("[-]AppPath: {}".format(self.target_app_path))
        if not os.path.exists(self.target_app_path):
            raise Exception("{} not exist".format(self.app_name))

        self.info_plist_file_path = os.path.join(self.target_app_path, "Info.plist")
        self.frameworks_dir = os.path.join(self.target_app_path, "Frameworks")
        self.plugins_dir = os.path.join(self.target_app_path, "PlugIns")

    def run(self):
        pass

    def resign(self):
        """重签名当前执行路径下的.app文件"""
        current_path = os.getcwd()
        print(Logger.green("✅ resign info"))
        print("[-]CurrentPath: {}".format(current_path))
        print("[-]AppName: {}".format(self.app_name))

        info_plist_file_path = os.path.join(self.target_app_path, "Info.plist")
        if not os.path.exists(info_plist_file_path):
            raise Exception("{} 不存在Info.plist文件".format(self.app_name))

        # 提取描述文件的entitlements
        self._cms_embedded()

        # 注入 - dylib
        self._inject_dylib()

        # 签名 - frameworks
        if os.path.exists(self.frameworks_dir):
            self._pre_codesign_dylib()

        # 签名 - plugins
        if os.path.exists(self.plugins_dir):
            self._pre_codesign_plugins()

        # 签名 - app
        EBinTool.codesign_dylib(self.target_app_path, self.identity)

        # 压缩成ipa
        self._zip_app()

        # 打印App包信息
        self._print_app_info()

        if self.install_type is not None:
            # 安装 - app
            EBinTool.install_app(self.target_app_path)

    def _cms_embedded(self):
        # security cms -D -i embedded.mobileprovision > entitlements.plist
        print(Logger.green("✅ cms embedded"))
        if not os.path.exists(self.mobileprovision_path):
            raise Exception("mobileprovision not exist")
        os.chdir(ESIGN_DIR_PATH)

        entitlements_file = os.path.join(ESIGN_DIR_PATH, EMBEDDED_ENTITLEMENTS)
        if os.path.exists(entitlements_file):
            os.remove(entitlements_file)

        profile_plist = os.path.join(ESIGN_DIR_PATH, PROFILE_PLIST)
        if os.path.exists(profile_plist):
            os.remove(profile_plist)

        print(
            "[-]security cms -D -i => {} > {}".format(
                PROFILE_PLIST, self.mobileprovision_path
            )
        )
        self._execute_shell(
            "security cms -D -i {} > {}".format(
                PROFILE_PLIST, self.mobileprovision_path
            )
        )
        self._execute_shell(
            "/usr/libexec/PlistBuddy -x -c 'Print :Entitlements' {} > {}".format(
                PROFILE_PLIST, EMBEDDED_ENTITLEMENTS
            )
        )
        self._execute_shell(
            "cp -rf "
            + self.mobileprovision_path
            + " "
            + "{}/embedded.mobileprovision".format(self.target_app_path)
        )

        os.chdir(self.current_path)
        print("[-]cms embedded done")

    def _inject_dylib(self):
        # /usr/libexec/PlistBuddy -c "Print :CFBundleName" "${INFOPLIST}"
        # optool install -c load -p "@executable_path/RedEnvelop.dylib" -t WeChat
        print(Logger.green("✅ inject dylib"))
        print("[-]dylibs => {}".format(self.dylibs))
        print("[-]Info.plist path => {}".format(self.info_plist_file_path))
        if len(self.dylibs) == 0:
            print(Logger.yellow("⚠️  Warn: no dylibs need to inject"))
            return

        def _inject_action(dylib_path):
            if not os.path.exists(dylib_path):
                print("inject fail: {}.framework not exit".format(dylib))
                return

            dylib_name, extension = os.path.splitext(dylib_path)
            print("[-]inject dylib => {}".format(dylib_name))
            bundle_name = subprocess.getoutput(
                '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
                    self.info_plist_file_path
                )
            )
            execu_table_path = os.path.join(self.target_app_path, bundle_name)
            app_frameworks_path = os.path.join(self.target_app_path, "Frameworks")
            if not os.path.exists(app_frameworks_path):
                os.makedirs(app_frameworks_path)
            dylib_framework_path = os.path.join(app_frameworks_path, dylib)
            print("[-]execu_table_path => {}".format(execu_table_path))
            print("[-]app_frameworks_path => {}".format(app_frameworks_path))
            print("[-]dylib_framework_path => {}".format(dylib_framework_path))

            if os.path.exists(dylib_framework_path):
                print("[-]update dylib => {}".format(dylib_name))
                self._execute_shell(f"rm -rf {dylib_framework_path}")
            self._execute_shell(f"cp -rf {dylib_framework_path} {app_frameworks_path}")

            optool_cmd_result = EBinTool.optool_inject(dylib_path, execu_table_path)
            print("{}".format(optool_cmd_result))
            if "Successfully" not in optool_cmd_result:
                raise Exception("optool inject dylibs fail")
            self._execute_shell("chmod +x {}".format(execu_table_path))

        for dylib in self.dylibs:
            _inject_action(dylib)

    def _pre_codesign_dylib(self):
        print(Logger.green("👉🏻 begin codesigning frameworks"))
        frameworks = []
        for root, dirs, files in os.walk(self.frameworks_dir):
            frameworks = dirs
            break
        for framework in frameworks:
            framework_mach_o = os.path.splitext(framework)[0]
            framework_mach_o_path = (
                self.frameworks_dir + os.sep + framework + os.sep + framework_mach_o
            )
            EBinTool.codesign_dylib(framework_mach_o_path, self.identity)

    def _pre_codesign_plugins(self):
        print(Logger.green("👉🏻 begin codesigning plugins"))
        plugins = []
        for root, dirs, files in os.walk(self.plugins_dir):
            plugins = dirs
            break
        for plugin in plugins:
            plugin_mach_o = os.path.splitext(plugin)[0]
            plugin_mach_o_path = (
                self.plugins_dir + os.sep + plugin + os.sep + plugin_mach_o
            )
            EBinTool.codesign_dylib(plugin_mach_o_path, self.identity)

    def _zip_app(self):
        print(Logger.green("✅ zip app to ipa"))
        print("[-]CurrentPath => {}".format(self.current_path))
        payload_path = os.path.join(self.current_path, "Payload")
        if os.path.exists(payload_path):
            os.system("rm -rf {}".format(payload_path))
        os.makedirs(payload_path)
        os.system("cp -rf {} {}".format(self.target_app_path, payload_path))
        stem, suffix = os.path.splitext(os.path.basename(self.app_name))
        zip_cmd = "zip -qr {}.ipa {}".format(stem, "Payload/")
        os.chdir(self.current_path)
        os.system(zip_cmd)

    def _print_app_info(self):
        bundle_name = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleName"  {}'.format(
                self.info_plist_file_path
            )
        )
        bundle_id = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier"  {}'.format(
                self.info_plist_file_path
            )
        )
        short_version = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString"  {}'.format(
                self.info_plist_file_path
            )
        )
        executable_name = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
                self.info_plist_file_path
            )
        )
        print(Logger.green("✅ app info"))
        print("[-]BundleName => {}".format(bundle_name))
        print("[-]BundleID => {}".format(bundle_id))
        print("[-]ShortVersion => {}".format(short_version))
        print("[-]ExecutableName => {}".format(executable_name))

    def _execute_shell(command_string):
        subprocess.call(command_string, shell=True)


if __name__ == "__main__":
    target_app_path = "/Users/apple/Downloads/Payload/sacurity.app"
    dylib_name, extension = os.path.splitext(target_app_path)
    dylib_extension = extension[1:]
    print("[-]inject dylib_name => {}".format(dylib_name))
    print("[-]inject dylib_name => {}".format(dylib_extension))
