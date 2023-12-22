import os
import getpass
import shutil
import subprocess
import configparser
from pathlib import Path
import re
from esign.elogger import Logger


class ESign(object):
    def __init__(self, args):
        pass


out_str = "/Out/"
package_file_name = "PackageConfig.json"
user_name = getpass.getuser()
vsscli_dir = "/Users/" + user_name + "/.esign/"
config_path = os.path.join(vsscli_dir, "settings.ini")
config_path = "../regign/settings.ini"
debug_codesigning_identity = "34B2B4FAF71A01ABDFF8E7D4BF7B147B6BDC1740"
release_codesigning_identity = "BFA68156479D4CA4F0FFE98B4188862FEC3CA259"
CODESIGNING_IDENTITY = debug_codesigning_identity

dev_embedded = "dev_embedded.mobileprovision"
dis_embedded = "dis_embedded.mobileprovision"
EMBEDDED_MOBILEPROVISION = dev_embedded

dev_entitlements = "dev_entitlements.plist"
dis_entitlements = "dis_entitlements.plist"
EMBEDDED_ENTITLEMENTS = "entitlements.plist"


################################【运行检测】#################################
def check_run_env(args):
    config_path = "/Users/apple/Desktop/WorkSpace/vss/build/lib/settings.ini"
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8-sig")

    sign_identity = config.get("USER", "debug_codesigning_identity")
    if not sign_identity:
        _execute_shell("security find-identity -v -p codesigning")
        sign_identity = input("请输入证书identitie值:")
        config.set("USER", "debug_codesigning_identity", sign_identity)
        with open(config_path, "w", encoding="utf-8-sig") as f:
            config.write(f)
        return False

    up_path = config.get("USER", "upgrade_path")
    if not up_path:
        up_path = input("请输入仓库文件夹路径:")
        config.set("USER", "upgrade_path", up_path)
        with open(config_path, "w", encoding="utf-8-sig") as f:
            config.write(f)
        return False

    embedded_path = config.get("USER", "embedded_mobileprovision_path")
    if not embedded_path:
        embedded_path = input("请输入描述文件路径:")
        config.set("USER", "embedded_mobileprovision_path", embedded_path)
        with open(config_path, "w", encoding="utf-8-sig") as f:
            config.write(f)
        if os.path.exists(embedded_path):
            shutil.copy(embedded_path, os.path.join(vsscli_dir, dev_embedded))

    return True


################################【重签名】#################################
def do_resign(app_name, is_release, is_reinstall, dylibs=[], is_create_ipa=False):
    """重签名当前执行路径下的.app文件"""
    current_path = os.getcwd()
    print(Logger.green("✅ resign info"))
    print("[-]CurrentPath: {}".format(current_path))
    print("[-]AppName: {}".format(app_name))
    target_app_path = current_path + os.sep + app_name
    if "/Users/" in app_name:
        target_app_path = app_name

    print("[-]AppPath: {}".format(target_app_path))
    if not os.path.exists(target_app_path):
        raise Exception("{} not exist".format(app_name))
    if is_release:
        global CODESIGNING_IDENTITY
        CODESIGNING_IDENTITY = release_codesigning_identity
        global EMBEDDED_MOBILEPROVISION
        EMBEDDED_MOBILEPROVISION = dis_embedded
        # global EMBEDDED_ENTITLEMENTS
        # EMBEDDED_ENTITLEMENTS = dis_entitlements
    print("[-]Configuration: {}".format(is_release))

    global IS_REINSTALL
    IS_REINSTALL = is_reinstall
    print("[-]IsReInstall: {}".format(is_reinstall))

    info_plist_file_path = target_app_path + os.sep + "Info.plist"
    if not os.path.exists(info_plist_file_path):
        raise Exception("{} 不存在Info.plist文件".format(app_name))

    # print(vsscli_dir)

    # 提取描述文件的entitlements
    _cms_embedded(target_app_path)

    # 注入 - dylib
    _inject_dylib(dylibs, info_plist_file_path, target_app_path)

    # 签名 - frameworks
    frameworks_dir = target_app_path + os.sep + "Frameworks"
    if os.path.exists(frameworks_dir):
        _pre_codesign_dylib(frameworks_dir)

    # 签名 - plugins
    plugins_dir = target_app_path + os.sep + "PlugIns"
    if os.path.exists(plugins_dir):
        _pre_codesign_plugins(plugins_dir)

    # 签名 - app
    _codesign_app(target_app_path)

    # 压缩成ipa
    _zip_app(is_create_ipa, current_path, target_app_path, app_name)

    # 打印App包信息
    _print_app_info(info_plist_file_path)

    # 安装 - app
    _install_app(target_app_path)


def _cms_embedded(target_app_path):
    # security cms -D -i embedded.mobileprovision > entitlements.plist
    current_path = os.getcwd()
    print(Logger.green("✅ cms embedded"))
    embedded_file = vsscli_dir + EMBEDDED_MOBILEPROVISION
    if not os.path.exists(embedded_file):
        raise Exception("{} not exist".format(EMBEDDED_MOBILEPROVISION))
    os.chdir(vsscli_dir)

    entitlements_file = vsscli_dir + EMBEDDED_ENTITLEMENTS
    if os.path.exists(entitlements_file):
        os.remove(entitlements_file)

    profile_plist = vsscli_dir + "profile.plist"
    if os.path.exists(profile_plist):
        os.remove(profile_plist)

    print(
        "[-]security cms -D -i => {} > profile.plist".format(EMBEDDED_MOBILEPROVISION)
    )
    _execute_shell(
        "security cms -D -i {} > profile.plist".format(EMBEDDED_MOBILEPROVISION)
    )
    _execute_shell(
        "/usr/libexec/PlistBuddy -x -c 'Print :Entitlements' profile.plist > {}".format(
            EMBEDDED_ENTITLEMENTS
        )
    )

    if not os.path.exists(entitlements_file):
        raise Exception("{} not exist".format(EMBEDDED_ENTITLEMENTS))
    _execute_shell(
        "cp "
        + embedded_file
        + " "
        + "{}/embedded.mobileprovision".format(target_app_path)
    )

    os.chdir(current_path)
    print("[-]cms embedded done")


def _zip_app(is_create_ipa, current_path, target_app_path, app_name):
    if is_create_ipa == False:
        return
    print(Logger.green("✅ zip app to ipa"))
    print("[-]CurrentPath => {}".format(current_path))
    payload_path = "{}/Payload".format(current_path)
    if os.path.exists(payload_path):
        os.system("rm -rf {}".format(payload_path))
    os.makedirs(payload_path)
    os.system("cp -rf {} {}".format(target_app_path, payload_path))
    stem, suffix = os.path.splitext(os.path.basename(app_name))
    zip_cmd = "zip -qr {}.ipa {}".format(stem, "Payload/")
    os.chdir(current_path)
    os.system(zip_cmd)


def _print_app_info(info_plist_file_path):
    bundle_name = subprocess.getoutput(
        '/usr/libexec/PlistBuddy -c "Print :CFBundleName"  {}'.format(
            info_plist_file_path
        )
    )
    bundle_id = subprocess.getoutput(
        '/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier"  {}'.format(
            info_plist_file_path
        )
    )
    short_version = subprocess.getoutput(
        '/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString"  {}'.format(
            info_plist_file_path
        )
    )
    executable_name = subprocess.getoutput(
        '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
            info_plist_file_path
        )
    )
    print(Logger.green("✅ app info"))
    print("[-]BundleName => {}".format(bundle_name))
    print("[-]BundleID => {}".format(bundle_id))
    print("[-]ShortVersion => {}".format(short_version))
    print("[-]ExecutableName => {}".format(executable_name))


def _install_app(target_app_path):
    print(Logger.green("✅ install app"))
    print("[-]AppPath => {}".format(target_app_path))
    install_type = "-b"
    if IS_REINSTALL:
        install_type = "-rb"
    install_cmd = "{}bin/ios-deploy_new {} {}".format(
        vsscli_dir, install_type, target_app_path
    )
    print("[-]".format(install_cmd))
    os.system(install_cmd)


def _codesign_app(target_app_path):
    entitlements_file = vsscli_dir + EMBEDDED_ENTITLEMENTS
    print(Logger.green("👉🏻 begin codesigning app"))
    print("[-]AppPath => {}".format(target_app_path))
    print("[-]CodesigningIdentity => {}".format(CODESIGNING_IDENTITY))
    codesign_cmd = "codesign -f -s {} --entitlements {} {}".format(
        CODESIGNING_IDENTITY, entitlements_file, target_app_path
    )
    codesign_cmd_result = subprocess.getoutput(codesign_cmd)
    print("{}".format(codesign_cmd_result))


def _inject_dylib(dylibs, info_plist_file_path, target_app_path):
    # /usr/libexec/PlistBuddy -c "Print :CFBundleName" "${INFOPLIST}"
    # optool install -c load -p "@executable_path/RedEnvelop.dylib" -t WeChat
    print(Logger.green("✅ inject dylib"))
    print("[-]dylibs => {}".format(dylibs))
    print("[-]Info.plist path => {}".format(info_plist_file_path))
    if len(dylibs) == 0:
        print(Logger.yellow("⚠️  Warn: no dylibs need to inject"))
        return

    def _inject_action(dylib):
        print("[-]inject dylib => {}".format(dylib))
        bundle_name = subprocess.getoutput(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable"  {}'.format(
                info_plist_file_path
            )
        )
        execu_table_path = "{}/{}".format(target_app_path, bundle_name)
        app_frameworks_path = "{}/Frameworks".format(target_app_path)
        dylib_framework_path = "{}/{}.framework".format(app_frameworks_path, dylib)
        vss_path = "{}Frameworks/{}.framework".format(vsscli_dir, dylib)
        print("[-]execu_table_path => {}".format(execu_table_path))
        print("[-]app_frameworks_path => {}".format(app_frameworks_path))
        print("[-]dylib_framework_path => {}".format(dylib_framework_path))

        if os.path.exists(dylib_framework_path):
            print("[-]update dylib => {}".format(dylib))
            _execute_shell("rm -rf {}".format(dylib_framework_path))
            _execute_shell("cp -rf {} {}".format(vss_path, app_frameworks_path))
            return

        if not os.path.exists(app_frameworks_path):
            os.makedirs(app_frameworks_path)
        if not os.path.exists(vss_path):
            print("inject fail: {}.framework not exit".format(dylib))
            return

        optool_cmd = '{}bin/optool install -c load -p "@executable_path/Frameworks/{}.framework/{}" -t {}'.format(
            vsscli_dir, dylib, dylib, execu_table_path
        )
        _execute_shell("cp -rf {} {}".format(vss_path, app_frameworks_path))
        optool_cmd_result = subprocess.getoutput(optool_cmd)
        print("{}".format(optool_cmd_result))
        if "Successfully" not in optool_cmd_result:
            raise Exception("optool inject dylibs fail")
        _execute_shell("chmod +x {}".format(execu_table_path))

    for dylib in dylibs:
        _inject_action(dylib)


def _pre_codesign_dylib(frameworks_dir):
    print(Logger.green("👉🏻 begin codesigning frameworks"))
    frameworks = []
    for root, dirs, files in os.walk(frameworks_dir):
        frameworks = dirs
        break
    for framework in frameworks:
        framework_mach_o = os.path.splitext(framework)[0]
        framework_mach_o_path = (
            frameworks_dir + os.sep + framework + os.sep + framework_mach_o
        )
        _codesign_dylib(framework_mach_o_path)


def _pre_codesign_plugins(plugins_dir):
    print(Logger.green("👉🏻 begin codesigning plugins"))
    plugins = []
    for root, dirs, files in os.walk(plugins_dir):
        plugins = dirs
        break
    for plugin in plugins:
        plugin_mach_o = os.path.splitext(plugin)[0]
        plugin_mach_o_path = plugins_dir + os.sep + plugin + os.sep + plugin_mach_o
        _codesign_dylib(plugin_mach_o_path)


def _codesign_dylib(dst):
    if not os.path.exists(dst):
        print("{} => not exist".format(dst))
    print("[-]codesigning dylibs => {}".format(dst))
    codesign_cmd = "codesign -f -s {} {}".format(CODESIGNING_IDENTITY, dst)
    codesign_cmd_result = subprocess.getoutput(codesign_cmd)
    print("{}".format(codesign_cmd_result))


def _execute_shell(command_string):
    subprocess.call(command_string, shell=True)
    # os.system(command_string)


def xml_from_mp_text(mp_text: str):
    """
    从mobileprovision文件内容里，提取出plist部分的字符串；
    效果如同以下命令：
        security cms -D -i embedded.mobileprovision > temp.plist

    :param mp_text: mobileprovision文件内容
    :return: plist部分的字符串内容
    """
    p_start = re.escape("<?xml")
    p_end = re.escape("</plist>")
    pattern_str = f"{p_start}.+{p_end}"
    result = re.search(pattern_str, mp_text, flags=re.DOTALL)
    xml_content = result.group()
    return xml_content


def content(file_path):
    """
    从mobileprovision文件里提取出plist部分的字符串内容；
    效果如同以下命令：
        security cms -D -i embedded.mobileprovision > temp.plist

    :param file_path: mobileprovision文件路径
    :return: plist部分的字符串内容
    """
    file_content = Path(file_path).read_text(encoding="ascii", errors="ignore")
    return xml_from_mp_text(file_content)


def get_app_id(file_path):
    """
    从mobileprovision文件里提取出AppID；
    效果如同以下命令：
        security cms -D -i embedded.mobileprovision > temp.plist
        /usr/libexec/PlistBuddy -c "Print :Entitlements:application-identifier" temp.plist

    :param file_path: mobileprovision文件路径
    :return: AppID
    """
    xml_content = content(file_path)
    app_id = re.search(
        "<key>application-identifier</key>\s*<string>(.+)</string>", xml_content
    ).group(1)
    return app_id


def get_entitlements(file_path):
    """
    从mobileprovision文件里提取出Entitlements；
    效果如同以下命令：
        security cms -D -i embedded.mobileprovision > temp.plist
        /usr/libexec/PlistBuddy -x -c "Print :Entitlements" temp.plist

    :param file_path: mobileprovision文件路径
    :return: Entitlements
    """
    xml_content = content(file_path)
    entitlements = re.search(
        "<key>Entitlements</key>\s*<dict>(.+)</dict>", xml_content, flags=re.DOTALL
    ).group(1)
    return entitlements
