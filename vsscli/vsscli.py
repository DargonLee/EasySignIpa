#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import getpass
import shutil
import subprocess
from .exec_tool import Logger
from .exec_frida import listApplicationDir

out_str = "/Out/"
package_file_name = "PackageConfig.json"
user_name = getpass.getuser()
vsscli_dir = "/Users/" + user_name + "/.vss_cli/"
debug_codesigning_identity = "34B2B4FAF71A01ABDFF8E7D4BF7B147B6BDC1740"
release_codesigning_identity = "BFA68156479D4CA4F0FFE98B4188862FEC3CA259"
CODESIGNING_IDENTITY = debug_codesigning_identity

dev_embedded = "dev_embedded.mobileprovision"
dis_embedded = "dis_embedded.mobileprovision"
EMBEDDED_MOBILEPROVISION = dev_embedded

dev_entitlements = "dev_entitlements.plist"
dis_entitlements = "dis_entitlements.plist"
EMBEDDED_ENTITLEMENTS = "entitlements.plist"


################################【初始化组件索引库】#################################
def init_cocoapods_repo(init_args):
    # init_args = True
    file_base = "/Users/" + user_name + "/.cocoapods/repos/"
    dir_array = os.listdir(file_base)
    print("当前repo环境：{}".format(dir_array))
    cocoapods_path = file_base + "cocoapods"
    if "cocoapods" in dir_array:
        os.chdir(file_base)
        _execute_shell("pwd")
        _execute_shell("rm -rf cocoapods/")
        _execute_shell("rm -rf 1-cocoapods/")
    _execute_shell(
        "pod repo add cocoapods ssh://ioscoder@gerrit.zhizhangyi.com:29418/core/ios/cocopodsSpec"
    )
    if os.path.exists(cocoapods_path):
        print("🚀初始化cocoapods repo环境完成🚀")
    else:
        print("❌初始化cocoapods repo环境失败❌")


################################【创建组件库】#################################
def create_temlate(name):
    """创建cocoapods模版"""
    # createCommand = "pod lib create {}".format(name)
    createCommand = "pod lib create {} --template-url=https://github.com/DargonLee/pod-template.git".format(
        name
    )
    os.system(createCommand)
    current_path = os.getcwd()
    old_path = current_path + "/" + name
    new_path = old_path + "_temp"
    os.renames(old_path, new_path)
    os.system("cp -r {}/* {}".format(new_path, current_path))
    os.system("rm -rf {}".format(new_path))


################################【发布单个组件库】#################################
def upload_cocoapods(podspec_name):
    """更新版本到cocoapods私有库"""
    # os.system('git stash')
    # os.system('git pull origin develop --tags')
    # os.system('git stash pop')
    podspec_string = "{}.podspec".format(podspec_name)
    version_string = subprocess.getoutput(
        "grep -E 's.version.*=' {}".format(podspec_string)
    )
    version_string = str(version_string)
    version_string_list = version_string.split()
    version_string = version_string_list[2].replace("'", "")
    remote_tag = subprocess.getoutput(
        "git describe --tags `git rev-list --tags --max-count=1`"
    )
    if version_string == remote_tag:
        print("当前版本远程已存在,请核对{}.podspec文件的版本信息是否正确".format(podspec_name))
        return
    os.system("git tag -m '{}' {}".format(version_string, version_string))
    os.system("git push origin {}".format(version_string))

    # lint_result = lint_podspec_file(podspec_name)
    lint_result = lint_git_status()
    if lint_result:
        upload_podspec_file(podspec_name, version_string)
        os.system("pod repo update")
        print("🚀🚀🚀{}的{}版本更新完成🚀🚀🚀".format(podspec_name, version_string))
    else:
        print("{}库还没提交到远程仓库，请提交后重试。".format(podspec_name))


def lint_git_status():
    status_string = subprocess.getoutput("git status")
    if "nothing to commit" in status_string:
        return True
    return False


def lint_podspec_file(podspec_name):
    """
    验证podspec文件是否符合规范
    pod lib lint --sources='ssh://lihailong@192.168.1.29:29418/core/ios/cocopodsSpec'
    --use-libraries --allow-warnings --verbose --no-clean | xcpretty"""
    old_path = os.getcwd()
    file_base = "/Users/" + user_name + "/.cocoapods/repos/cocopodsSpec/"
    os.chdir(file_base)
    origin_url = subprocess.getoutput("git remote -v")
    source_url = origin_url.split(" ")[1]
    target_url = source_url[15:]
    lint_result = os.system(
        "pod lib lint --sources='{}' --use-libraries --allow-warnings --no-clean | xcpretty".format(
            target_url
        )
    )
    lint_result_bool = True
    if "passed validation" in lint_result:
        print("lint successfule")
    else:
        lint_result_bool = False
        print("{}.podspec 文件验证失败，请根据提示进行修改后再次验证提交".format(podspec_name))
    os.chdir(old_path)
    return lint_result_bool


def upload_podspec_file(podspec_name, version_string):
    """提交podspec文件到远程仓库"""
    user_name = getpass.getuser()
    file_base = "/Users/" + user_name + "/.cocoapods/repos/cocopodsSpec/"
    file_dir = file_base + podspec_name
    file_name = file_dir + "/" + version_string
    if os.path.exists(file_name):
        shutil.rmtree(file_name)
    os.makedirs(file_name)
    filename = "{}.podspec".format(podspec_name)
    shutil.copy(filename, file_name)
    os.chdir(file_base)
    # print(os.getcwd())

    os.system("git add .")
    os.system("git commit -am modification")
    os.system("git pull")
    os.system("git push origin develop:develop")


################################【发布所有组件库】#################################
def public_all_component(version_string):
    """一键发布所有组件库"""
    target_path = os.getcwd() + "/"
    # target_path = os.getcwd() + '/component/'
    if not "/component" in target_path:
        raise Exception("请检查脚本执行路径是否正确")
    choose_array = []
    path_array = []
    # 获取当前路径下的所有文件夹
    dir_array = os.listdir(target_path)
    dir_array.remove(".DS_Store")
    for item in dir_array:
        path_array.append(target_path + item)
        choose_array.append(item.capitalize())

    if len(choose_array) == 0 or len(path_array) == 0:
        raise Exception("当前执行路径文件夹为空")
    # 打印选项
    for i in range(0, len(choose_array)):
        print("\033[0;32;40m\t {} : {} \033[0m".format(i, choose_array[i]))

    input_array = input("请输入需要发布的索引号并以空格分割：")
    result_array = str(input_array).split(" ")
    # 参数校验
    for item in result_array:
        print(item)
        index = int(item)
        if index > int(len(choose_array) - 1):
            raise Exception("请检查输入数字是否正确")

    print("✅ 参数校验成功开始处理...")
    for item in result_array:
        index = int(item)
        print("=> 开始处理:{} 版本好:{}".format(path_array[index], version_string))
        modify_podspec_version(path_array[index], version_string)


def modify_podspec_version(target_path, version):
    os.chdir(target_path)
    file_name = os.path.basename(target_path).capitalize()
    target_file = file_name + ".podspec"
    # 获取老的版本号 grep -E 's.version.*=' CTMediator.podspec
    old_version_string = subprocess.getoutput(
        "grep -E 's.version.*=' {}".format(target_file)
    )
    old_version_string = str(old_version_string)
    version_string_list = old_version_string.split()
    old_version_string = version_string_list[2].replace("'", "")

    result = _compareVersion(version, old_version_string)
    if result != 1:
        raise Exception("发布的版本不能小于当前版本")

    # 获取行号 grep -nE 's.version.*=' emmlib.podspec | cut -d : -f1
    line_number = subprocess.getoutput(
        "grep -nE 's.version.*=' " + str(target_file) + " | cut -d : -f1"
    )
    # sed -i "" "${line_number}s/${VersionNumber}/${NewVersionNumber}/g" CTMediator.podspec
    subprocess.getoutput(
        'sed -i "" "{}s/{}/{}/g" {}'.format(
            line_number, old_version_string, version, target_file
        )
    )
    print("🚀 {} 更新中...".format(file_name))

    os.system("git add .")
    os.system("git commit -am modification")
    os.system("git pull")
    os.system("git push origin develop:develop")
    upload_podspec_file(file_name, version)

    print("✅ {}版本更新完成 {} => {}".format(target_file, old_version_string, version))


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


################################【发布Vss版本】#################################
def publich_vss(version):
    target_path = os.getcwd()
    dir_array = os.listdir(target_path)
    if ".repo" not in dir_array or "framework" not in dir_array:
        raise Exception("请检查脚本执行路径是否正确")
    ask_str = input(Logger.green("确定发布的版本号为：{} (Y/n)\n".format(version)))
    if ask_str == "Y":
        # 发布Vss
        vss_path = target_path + "/framework/vss"
        os.chdir(vss_path)
        _execute_shell("git checkout -b {}".format(version))
        _execute_shell("git push origin {}:{}".format(version, version))

        # 发布repo
        repo_path = target_path + "/.repo/manifests"
        os.chdir(repo_path)
        repo_version = "vss_".format(version)
        _execute_shell("git checkout -b {}".format(repo_version))
        _execute_shell("sed -i '' '6s/develop/{}/g' scene_jenkins.xml".format(version))
        _execute_shell("git add .")
        _execute_shell('git commit -m "publish {}"'.format(version))
        _execute_shell("git push origin {}:{}".format(repo_version, repo_version))
        _execute_shell("git checkout develop")

        # Done
        print("🚀 Public Vss {} Done".format(version))
        os.chdir(target_path)
    else:
        print("此次发布已取消")


################################【frida】#################################
def frida_listApplicationDir(args):
    listApplicationDir(args)


def _execute_shell(command_string):
    subprocess.call(command_string, shell=True)
    # os.system(command_string)


# 对比版本号大小
# 1 第一个参数大于第二个
# -1 第一个参数小于第二个
# 0 相等
def _compareVersion(version1, version2):
    def split_and_2_int(lst):
        """
        将字符串按照“.”分割，并将每部分转成数字
        :param lst:
        :return:
        """
        lst = lst.split(".")
        return [int(n) for n in lst]

    def just_two_lists(lst1, lst2):
        """
        如果两个数字列表长度不一，需要将短一点的列表末尾补零，让它们长度相等
        :param lst1:
        :param lst2:
        :return:
        """
        l1, l2 = len(lst1), len(lst2)
        if l1 > l2:
            lst2 += [0] * (l1 - l2)
        elif l1 < l2:
            lst1 += [0] * (l2 - l1)
        return lst1, lst2

    def compare_version_lists(v1_lst, v2_lst):
        """
        比较版本号列表，从高位到底位逐位比较，根据情况判断大小。
        :param v1_lst:
        :param v2_lst:
        :return:
        """
        for v1, v2 in zip(v1_lst, v2_lst):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0

    # 预处理版本号
    version1, version2 = just_two_lists(
        split_and_2_int(version1), split_and_2_int(version2)
    )
    return compare_version_lists(version1, version2)
