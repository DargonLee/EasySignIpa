import os
import shutil
import subprocess
from esign.eprovision import EProvision
from esign.ezip import EZipFile
from esign.elogger import Logger
from esign.econfig import EConfigHandler
from esign.ebin import EBinTool
from esign.utils import (
    SETTINGS_PATH,
    PROVISIONS_DIR_PATH,
    ESIGN_DIR_PATH,
    PROFILE_PLIST,
    EMBEDDED_ENTITLEMENTS,
)


class ESigner(object):
    def __init__(self):
        self.install_type = None
        self.inject_dylib_list = None
        self.target_app_path = None
        self.payload_path = None
        self.after_payload_path = None
        self.app_name = None
        self.identity = None
        self.mobileprovision_path = None
        self.tempdir = None
        self.current_path = None
        self.provision = None

        self.config = EConfigHandler(SETTINGS_PATH)
        self.identity = self.config.get_identity() or None
        self.mobileprovision_path = self.config.get_mobileprovision_path() or None
        if self.mobileprovision_path:
            self.provision = EProvision(self.mobileprovision_path)

    @property
    def mobileprovision(self):
        file_name_with_extension = os.path.basename(self.mobileprovision_path)
        return file_name_with_extension

    def check_identity(self):
        self.identity = self.config.get_identity()
        if not self.identity:
            self.set_identity()

    def set_identity(self):
        self._execute_shell("security find-identity -v -p codesigning")
        self.identity = input(Logger.green("Please select the identity value for the certificate :"))
        self.config.set_identity(self.identity)
        print('[-]setEnv: identity => {}'.format(self.identity))

    def check_mobileprovision(self):
        self.mobileprovision_path = self.config.get_mobileprovision_path()
        if not self.mobileprovision_path:
            self.set_mobileprovision()
        self.provision = EProvision(self.mobileprovision_path)

    def set_mobileprovision(self):
        self.mobileprovision_path = input(
            Logger.green("Please provide the full path to the provisioning profile file :"))
        if not os.path.exists(self.mobileprovision_path):
            raise Exception(f"{self.mobileprovision_path} not exist")
        shutil.copy(self.mobileprovision_path, PROVISIONS_DIR_PATH)
        self.config.set_mobileprovision_path(self.mobileprovision_path)
        print(f'[-]setEnv: mobileprovision => {self.mobileprovision}')

    def set_run_env(self):
        self.set_identity()
        self.set_mobileprovision()
        result = self.provision.contain_cer_identity(self.identity)
        print(f'[-]setEnv: result => {result}')
        return result

    def check_run_env(self):
        self.check_identity()
        self.check_mobileprovision()
        return self.provision.contain_cer_identity(self.identity)

    def _prepare_app_path(self):
        print(Logger.green("✅ prepare app"))

        self.current_path = os.getcwd()
        print(f"[-]prepare: current_path => {self.current_path}")

        app_path, extension = os.path.splitext(self.target_app_path)
        app_extension = extension[1:]
        app_name = os.path.basename(app_path)
        self.app_name = app_name

        if not os.path.exists(self.target_app_path):
            print(f"[-]Error: {self.target_app_path} does not exist.")
            exit(1)
        if app_extension != "ipa" and app_extension != "app":
            print(f"[-]Error: {self.target_app_path} does not support.")
            exit(1)

        if app_extension == "ipa":
            import tempfile
            self.tempdir = tempfile.mkdtemp()
            EZipFile.unzip_file(self.target_app_path, self.tempdir)
            payload_path = os.path.join(self.tempdir, "Payload")
            self.payload_path = payload_path
            self.app_name = os.listdir(payload_path)[0]
            self.target_app_path = os.path.join(payload_path, self.app_name)
        else:
            self.tempdir = os.path.dirname(self.target_app_path)

        print(f"[-]prepare: AppPath => {self.target_app_path}")
        if not os.path.exists(self.target_app_path):
            raise Exception("{} not exist".format(self.app_name))

        self.info_plist_file_path = os.path.join(self.target_app_path, "Info.plist")
        self.frameworks_dir = os.path.join(self.target_app_path, "Frameworks")
        self.plugins_dir = os.path.join(self.target_app_path, "PlugIns")
        self.sc_info_dir = os.path.join(self.target_app_path, "SC_Info")
        self.watch_dir = os.path.join(self.target_app_path, "Watch")

        print(f"[-]prepare info_plist_file_path => : {self.info_plist_file_path}")
        print(f"[-]prepare frameworks_dir => : {self.frameworks_dir}")
        print(f"[-]prepare plugins_dir => : {self.plugins_dir}")
        print(f"[-]prepare target_app_path => : {self.target_app_path}")
        print(f"[-]prepare tempdir => : {self.tempdir}")

    def _check_resign_env(self):
        if not os.path.exists(self.info_plist_file_path):
            raise Exception(f"{self.app_name} Info.plist not exist")

    def resign(
            self,
            app_path,
            dylib_list=[],
            output_dir=None,
            install_type=None,
    ):
        self.target_app_path = app_path
        self.inject_dylib_list = dylib_list
        self.output_dir = output_dir
        self.install_type = install_type

        self._prepare_app_path()

        print(Logger.green("✅ resign info"))
        print("[-]resign: AppName: {}".format(self.app_name))

        # 检测重签环境
        self._check_resign_env()

        # 提取描述文件的entitlements
        self._cms_embedded()

        # 注入 - dylib
        if len(self.inject_dylib_list) > 0:
            self._inject_dylib()

        # 签名 - frameworks
        if os.path.exists(self.frameworks_dir):
            self._pre_codesign_dylib()

        # 删除 - plugins
        if os.path.exists(self.plugins_dir):
            shutil.rmtree(self.plugins_dir)
            # self._pre_codesign_plugins()

        # 删除 - SC_Info
        if os.path.exists(self.sc_info_dir):
            shutil.rmtree(self.sc_info_dir)

        # 删除 - Watch
        if os.path.exists(self.watch_dir):
            shutil.rmtree(self.watch_dir)

        # 签名 - app
        EBinTool.codesign_app(self.target_app_path, self.entitlements_file, self.identity)

        # 压缩成ipa
        if self.output_dir is not None:
            self._zip_app()

        # 打印App包信息
        self._print_app_info()

        # 安装 - app
        if self.install_type is not None:
            EBinTool.install_app(self.target_app_path)

        # clean tmp
        self._clean_tmp_files()

    def _clean_tmp_files(self):
        if self.after_payload_path is not None and os.path.exists(self.after_payload_path):
            shutil.rmtree(self.after_payload_path)

    def _cms_embedded(self):
        # security cms -D -i embedded.mobileprovision > entitlements.plist
        # print(Logger.green("✅ cms embedded"))
        # print(self.mobileprovision_path)
        if not os.path.exists(self.mobileprovision_path):
            raise Exception("mobileprovision not exist")

        self.entitlements_file = os.path.join(ESIGN_DIR_PATH, EMBEDDED_ENTITLEMENTS)
        if os.path.exists(self.entitlements_file):
            os.remove(self.entitlements_file)

        profile_plist = os.path.join(ESIGN_DIR_PATH, PROFILE_PLIST)
        if os.path.exists(profile_plist):
            os.remove(profile_plist)

        self._execute_shell(
            "security cms -D -i {} > {}".format(
                self.mobileprovision_path, profile_plist
            )
        )
        self._execute_shell(
            "/usr/libexec/PlistBuddy -x -c 'Print :Entitlements' {} > {}".format(
                profile_plist, self.entitlements_file
            )
        )
        self._execute_shell(
            "cp -rf "
            + self.mobileprovision_path
            + " "
            + "{}/embedded.mobileprovision".format(self.target_app_path)
        )

        print("[-]cms embedded done")

    def _inject_dylib(self):
        # /usr/libexec/PlistBuddy -c "Print :CFBundleName" "${INFOPLIST}"
        # optool install -c load -p "@executable_path/RedEnvelop.dylib" -t WeChat
        print(Logger.green("✅ inject dylib"))
        print("[-]dylibs => {}".format(self.inject_dylib_list))
        print("[-]Info.plist path => {}".format(self.info_plist_file_path))
        if len(self.inject_dylib_list) == 0:
            print(Logger.yellow("⚠️  Warn: no dylibs need to inject"))
            return

        def _inject_action(dylib_path):
            if not os.path.exists(dylib_path):
                raise Exception(f"[-]inject fail: {dylib_path}.framework not exit")

            dylib_framework_name = os.path.basename(dylib_path)
            dylib_name, extension = os.path.splitext(dylib_framework_name)
            dylib_extension = extension[1:]

            if dylib_extension == "framework":
                framework_name = os.path.join(dylib_framework_name, dylib_name)
            elif dylib_extension == "dylib":
                framework_name = dylib_framework_name
            else:
                raise Exception(f"[-]dylib_extension not support => {dylib_extension}")

            print(f"[-]inject dylib => {dylib_name}")
            bundle_name = subprocess.getoutput(
                '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
                    self.info_plist_file_path
                )
            )
            execu_table_path = os.path.join(self.target_app_path, bundle_name)
            app_frameworks_path = os.path.join(self.target_app_path, "Frameworks")
            if not os.path.exists(app_frameworks_path):
                os.makedirs(app_frameworks_path)
            dylib_framework_path = os.path.join(app_frameworks_path, dylib_framework_name)

            print(f"[-]execu_table_path => {execu_table_path}")
            print(f"[-]app_frameworks_path => {app_frameworks_path}")
            print(f"[-]dylib_framework_path => {dylib_framework_path}")

            if os.path.exists(dylib_framework_path):
                print(f"[-]update dylib => {dylib_name}")
                self._execute_shell(f"rm -rf {dylib_framework_path}")
            else:
                optool_cmd_result = EBinTool.optool_inject(framework_name, execu_table_path)
                print("{}".format(optool_cmd_result))
                if "Successfully" not in optool_cmd_result:
                    raise Exception("optool inject dylib_list fail")
                self._execute_shell(f"chmod +x {execu_table_path}")
            self._execute_shell(f"cp -rf {dylib_path} {app_frameworks_path}")

        for dylib in self.inject_dylib_list:
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
        payload_path = os.path.join(
            self.tempdir, "Payload"
        )
        payload_app_path = os.path.join(payload_path, os.path.basename(self.target_app_path))
        print(f"zip: payload_path {payload_app_path}")
        print(f"zip: tempdir {self.tempdir}")
        if os.path.exists(payload_app_path):
            shutil.rmtree(payload_app_path)
        shutil.copytree(self.target_app_path, payload_app_path)
        self.after_payload_path = payload_path
        os.chdir(self.tempdir)
        stem, suffix = os.path.splitext(os.path.basename(self.app_name))
        ipa_name = f"{stem}_resign.ipa"
        zip_cmd = "zip -qr {} {}".format(ipa_name, "Payload/")
        os.system(zip_cmd)
        shutil.move(
            os.path.join(self.tempdir, ipa_name),
            os.path.join(self.output_dir, ipa_name),
        )
        os.chdir(self.current_path)

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
        print(f"[-]BundleName => {bundle_name}")
        print(f"[-]BundleID => {bundle_id}")
        print(f"[-]ShortVersion => {short_version}")
        print(f"[-]ExecutableName => {executable_name}")

    def _execute_shell(self, command_string):
        subprocess.call(command_string, shell=True)


if __name__ == "__main__":
    target_app_path = "/Users/apple/Downloads/Payload/sacurity.app"
    tmp_path_ipa = "/Users/apple/Downloads/Payload/111.ipa"
    tmp_path_payload = "/Users/apple/Downloads/Payload/Payload"
    destination_path = "/Users/apple/Downloads/Payload/Payload/sacurity.app"
    dylib_name, extension = os.path.splitext(target_app_path)
    dylib_extension = extension[1:]
    print("[-]inject dylib_name => {}".format(dylib_name))
    print("[-]inject dylib_name => {}".format(dylib_extension))
