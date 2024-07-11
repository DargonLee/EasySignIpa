import json
import os
import shutil
import subprocess
import plistlib
from pathlib import Path

from esign.elogger import Logger
from esign.econfig import EConfigHandler
from esign.ebin import EBinTool
from esign.eprovision import EProvision
from esign.ezip import EZipFile
from esign.utils import (
    SETTINGS_PATH,
    PROVISIONS_DIR_PATH,
    ESIGN_DIR_PATH,
    PROFILE_PLIST,
    EMBEDDED_ENTITLEMENTS,
    EMBEDDED_ORI_ENTITLEMENTS,
    EMBEDDED_PRO_ENTITLEMENTS
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
        self.execute_path = None
        self.executable_name = None

        self.config = EConfigHandler(SETTINGS_PATH)

    def check_identity(self):
        if not self.config.get_identity():
            self._execute_shell("security find-identity -v -p codesigning")
            identity = input(Logger.green("Please select the [debug] identity value for the certificate :"))
            self.config.set_identity(identity)
            print('[*] SetEnv [debug] identity: {} success'.format(identity))

    def check_mobileprovision(self):
        mobileprovision_path = self.config.get_mobileprovision_path()
        if not mobileprovision_path:
            mobileprovision_path = input(
                Logger.green("Please provide the full path to the [debug] provisioning profile file :"))
            if not os.path.exists(mobileprovision_path):
                raise Exception(f"{mobileprovision_path} not exist")
            shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
            self.config.set_mobileprovision_path(mobileprovision_path)
            print(f'[*] SetEnv [debug] mobileprovision file success: {mobileprovision_path}')

    def check_release_identity(self):
        if not self.config.get_release_identity():
            self._execute_shell("security find-identity -v -p codesigning")
            identity = input(Logger.green("Please select the [release] identity value for the certificate :"))
            self.config.set_release_identity(identity)
            print('[*] SetEnv [release] identity: {} success'.format(identity))

    def check_release_mobileprovision(self):
        if not self.config.get_release_mobileprovision_path():
            mobileprovision_path = input(
                Logger.green("Please provide the full path to the [release] provisioning profile file :"))
            if not os.path.exists(mobileprovision_path):
                raise Exception(f"{mobileprovision_path} not exist")
            shutil.copy(mobileprovision_path, PROVISIONS_DIR_PATH)
            self.config.set_release_mobileprovision_path(mobileprovision_path)
            print(f'[*] SetEnv [release] mobileprovision file success: {mobileprovision_path}')

    def check_release_run_env(self):
        self.check_release_identity()
        self.check_release_mobileprovision()

    def check_run_env(self):
        self.check_identity()
        self.check_mobileprovision()

    def _prepare_app_path(self):
        print(Logger.blue("👉🏻 prepare app"))

        self.current_path = os.getcwd()
        print(f"[*] Prepare current path: {self.current_path}")

        app_path, extension = os.path.splitext(self.target_app_path)
        app_extension = extension[1:]
        app_name = os.path.basename(app_path)
        self.app_name = app_name

        if not os.path.exists(self.target_app_path):
            print(Logger.error(f"Error: {self.target_app_path} does not exist."))
            exit(1)
        if app_extension != "ipa" and app_extension != "app":
            print(Logger.error(f"[-]Error: {self.target_app_path} does not support."))
            exit(1)

        if app_extension == "ipa":
            import tempfile
            self.tempdir = tempfile.mkdtemp()
            EZipFile.unzip_file(self.target_app_path, self.tempdir)
            self.payload_path = os.path.join(self.tempdir, "Payload")
            tmp_list = os.listdir(self.payload_path)
            if len(tmp_list) == 2 and '.DS_Store' in tmp_list:
                tmp_list.remove('.DS_Store')
            self.app_name = tmp_list[0]
            self.target_app_path = os.path.join(self.payload_path, self.app_name)
        else:
            self.tempdir = os.path.dirname(self.target_app_path)
            payload_path = os.path.join(self.tempdir, "Payload")
            self.payload_path = payload_path

        print(f"[*] Prepare appPath: {self.target_app_path}")
        if not os.path.exists(self.target_app_path):
            raise Exception("{} not exist".format(self.app_name))

        self.info_plist_file_path = os.path.join(self.target_app_path, "Info.plist")
        self.frameworks_dir = os.path.join(self.target_app_path, "Frameworks")
        self.plugins_dir = os.path.join(self.target_app_path, "PlugIns")
        self.sc_info_dir = os.path.join(self.target_app_path, "SC_Info")
        self.watch_dir = os.path.join(self.target_app_path, "Watch")
        self.ds_store = os.path.join(self.payload_path, ".DS_Store")
        self.macosx = os.path.join(self.payload_path, "__MACOSX")
        self.code_signature = os.path.join(self.payload_path, "_CodeSignature")

        self.executable_name = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
                self.info_plist_file_path
            )
        )
        self.execute_path = os.path.join(self.target_app_path, self.executable_name)

        print(f"[*] Info plist file path: {self.info_plist_file_path}")
        print(f"[*] Frameworks dir: {self.frameworks_dir}")
        print(f"[*] Plugins dir: {self.plugins_dir}")
        print(f"[*] Target app path: {self.target_app_path}")
        print(f"[*] Tempdir: {self.tempdir}")

    def _check_resign_env(self):
        if not os.path.exists(self.info_plist_file_path):
            raise Exception(f"{self.app_name} Info.plist not exist")

    def resign(
            self,
            app_path,
            dylib_list=[],
            output_dir=None,
            install_type=None,
            is_print_info=False,
            bundle_id=None,
            bundle_name=None,
            build_configuration='debug',
    ):
        self.target_app_path = app_path
        self.inject_dylib_list = dylib_list
        self.output_dir = output_dir
        self.install_type = install_type
        self.bundle_id = bundle_id
        self.bundle_name = bundle_name
        self.build_configuration = build_configuration

        # 签名模式 debug ｜ release 检测
        build_status = build_configuration == 'debug'
        if build_status:
            self.check_run_env()
        else:
            self.check_release_run_env()


        # 证书和描述文件
        self.identity = self.config.get_identity() if build_status else self.config.get_release_identity()
        self.mobileprovision_path = self.config.get_mobileprovision_path() if build_status else self.config.get_release_mobileprovision_path()
        if self.mobileprovision_path:
            self.provision = EProvision(self.mobileprovision_path)
            result = self.provision.contain_cer_identity(self.identity)
            print(f'[*] SetEnv EProvision result: {result}')


        # app 签名准备
        self._prepare_app_path()
        print(Logger.green("✅ resign info"))
        print("[*] AppName: {}".format(self.app_name))

        # 检测重签环境
        self._check_resign_env()

        #资源处理
        # self._prepare_recourse()

        # 处理 Info.plist
        self._prepare_info_plist()

        # 删除 - unrestrict
        self._prepare_mach_o()

        # 提取描述文件的entitlements
        self._cms_embedded()

        # 注入 - dylib
        if len(self.inject_dylib_list) > 0:
            self._inject_dylib()

        # 签名 - frameworks
        if os.path.exists(self.frameworks_dir):
            self._pre_codesign_dylib()

        # 签名 - app
        EBinTool.codesign_app(self.target_app_path, self.entitlements_file, self.identity)

        # 压缩成ipa
        if self.output_dir is not None:
            self._zip_app()

        # 打印App包信息
        self._print_app_info()

        # 安装 - app
        if self.install_type:
            EBinTool.install_app(self.target_app_path, install_type)

        # 打印Info.plist文件所有内容
        if is_print_info:
            self._print_app_infoplist_content()

        # clean tmp
        self._clean_tmp_files()

    def _prepare_recourse(self):
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

        # 删除 - .DS_Store
        ds_file_path = Path(self.ds_store)
        if ds_file_path.is_file():
            os.remove(ds_file_path)

        # 删除 - __MACOSX
        if os.path.exists(self.macosx):
            shutil.rmtree(self.macosx)

        # 删除 - _CodeSignature
        if os.path.exists(self.code_signature):
            shutil.rmtree(self.code_signature)

    def _prepare_info_plist(self):
        # subprocess.getoutput(
        #     '/usr/libexec/PlistBuddy -c "Delete :UIDeviceFamily"  {}'.format(
        #         self.info_plist_file_path
        #     )
        # )

        print(Logger.blue("👉🏻 prepare_info_plist"))

        self.ori_bundle_id = subprocess.getoutput(
            f'/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "{self.info_plist_file_path}"').strip()
        print("[-]origin bundle id => {}".format(self.ori_bundle_id))

        self.ori_bundle_name = subprocess.getoutput(
            f'/usr/libexec/PlistBuddy -c "Print :CFBundleDisplayName" "{self.info_plist_file_path}"').strip()
        print("[-]origin bundle display name => {}".format(self.ori_bundle_name))

        if self.bundle_id:
            subprocess.getoutput(
                f'/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {self.bundle_id}" "{self.info_plist_file_path}"')
            print("[-]new bundle id => {}".format(self.bundle_id))

        if self.bundle_name:
            subprocess.getoutput(
                f'/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName {self.bundle_name}" "{self.info_plist_file_path}"')
            print("[-]new bundle display name is => {}".format(self.bundle_name))

    def _prepare_mach_o(self):
        EBinTool.optool_delete_unrestrict(self.execute_path)

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

        ori_entitlements_plist = os.path.join(ESIGN_DIR_PATH, EMBEDDED_ORI_ENTITLEMENTS)
        if os.path.exists(ori_entitlements_plist):
            os.remove(ori_entitlements_plist)

        EBinTool.dump_app_entitlements(self.target_app_path, ori_entitlements_plist)
        is_dump_appent_fail = False
        if not os.path.exists(ori_entitlements_plist):
            is_dump_appent_fail = True
            print(Logger.warning("dump app entitlements fail"))
        else:
            with open(ori_entitlements_plist, 'rb') as f:
                original_entitlements = plistlib.load(f)
                if len(original_entitlements) == 0:
                    is_dump_appent_fail = True
                    print(Logger.warning("dump app entitlements fail"))

        pro_entitlements_plist = os.path.join(ESIGN_DIR_PATH, EMBEDDED_PRO_ENTITLEMENTS)
        if os.path.exists(pro_entitlements_plist):
            os.remove(pro_entitlements_plist)
        self._execute_shell(
            "security cms -D -i {} > {}".format(
                self.mobileprovision_path, pro_entitlements_plist
            )
        )
        if not os.path.exists(pro_entitlements_plist):
            raise Exception("dump mobileprovision entitlements fail")
        with open(pro_entitlements_plist, 'rb') as f:
            original_entitlements = plistlib.load(f)
            if len(original_entitlements) == 0:
                raise Exception("dump mobileprovision entitlements fail")

        profile_plist = os.path.join(ESIGN_DIR_PATH, PROFILE_PLIST)
        if os.path.exists(profile_plist):
            os.remove(profile_plist)
        self._merge_entitlements(ori_entitlements_plist, pro_entitlements_plist, profile_plist, is_dump_appent_fail)
        if not os.path.exists(profile_plist):
            raise Exception("merge entitlements fail")

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

    def _merge_entitlements(self, original_file, pro_file, output_file, is_dump_appent_fail):

        with open(pro_file, 'rb') as f:
            pro_entitlements = plistlib.load(f)
        if not is_dump_appent_fail:
            with open(original_file, 'rb') as f:
                original_entitlements = plistlib.load(f)
            merged_entitlements = original_entitlements.copy()
            merged_entitlements.update(pro_entitlements)
        else:
            merged_entitlements = pro_entitlements.copy()

        with open(output_file, 'wb') as f:
            plistlib.dump(merged_entitlements, f)


    def _inject_dylib(self):
        # /usr/libexec/PlistBuddy -c "Print :CFBundleName" "${INFOPLIST}"
        # optool install -c load -p "@executable_path/RedEnvelop.dylib" -t WeChat
        print(Logger.green("✅ inject dylib"))
        print("[-]dylibs => {}".format(self.inject_dylib_list))
        print("[-]Info.plist path => {}".format(self.info_plist_file_path))
        if len(self.inject_dylib_list) == 0:
            print(Logger.yellow("⚠️ no dylibs need to inject"))
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

            print(f"[*] Inject dylib name: {dylib_name}")
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

            print(f"[*] Executable path: {execu_table_path}")
            print(f"[*] App Frameworks path: {app_frameworks_path}")
            print(f"[*] Dylib Framework path: {dylib_framework_path}")

            if os.path.exists(dylib_framework_path):
                print(f"[*] Update dylib: {dylib_name}")
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
        print(Logger.blue("👉🏻 begin codesigning frameworks"))
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
        print(Logger.green("✅ begin codesigning plugins"))
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
        print(f"[*] zip payload path: {payload_app_path}")
        print(f"[*] zip tempdir path: {self.tempdir}")
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

    def _print_app_infoplist_content(self):
        print(Logger.green("✅ app info plist content"))
        with open(self.info_plist_file_path, 'rb') as f:
            plist_content = plistlib.load(f)
            json_content = json.dumps(plist_content, indent=4, ensure_ascii=False)
            print(json_content)

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
        print(Logger.green("✅ app base info"))
        print(f"[*] BundleName: {bundle_name}")
        print(f"[*] BundleID: {bundle_id}")
        print(f"[*] ShortVersion: {short_version}")
        print(f"[*] ExecutableName: {executable_name}")

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
