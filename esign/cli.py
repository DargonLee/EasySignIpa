import argparse
from esign.app_signer import AppSigner
from esign.econfig import ConfigHandler
from esign.eupdate import EUpdate
from esign import __version__

def main():
    parser = argparse.ArgumentParser(description="IPA 重签名工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 签名命令
    sign_parser = subparsers.add_parser("sign", help="重签名 IPA 或 APP")
    sign_parser.add_argument('-s', '--sign', help='要重签名的 .ipa 或 .app 文件路径', type=str, required=True)
    sign_parser.add_argument('-l', '--inject', help='要注入的动态库路径', type=str, action='append')
    sign_parser.add_argument('-o', '--output', help='输出重签名后的 IPA 文件路径', type=str)
    sign_parser.add_argument('-r', '--release', help='使用发布证书签名', action='store_true')
    sign_parser.add_argument('--bundle_id', help='修改应用的 bundle ID', type=str)
    sign_parser.add_argument('--bundle_name', help='修改应用的显示名称', type=str)
    sign_parser.add_argument('--info', help='打印 Info.plist 内容', action='store_true')
    sign_parser.add_argument('--symbol', help='恢复符号表', action='store_true')

    # 安装命令
    sign_parser.add_argument('-d', '--device_id', help='指定安装设备的 ID', type=str)
    group_install = sign_parser.add_mutually_exclusive_group(required=True)
    group_install.add_argument('-b', '--basic_install', help='基本安装重签名后的 IPA 或 APP', action='store_true')
    group_install.add_argument('-rb', '--reinstall', help='卸载已存在的同名应用后再安装', action='store_true')

    # 更新命令
    update_parser = subparsers.add_parser("update", help="更新签名配置")
    update_parser.add_argument('-m', '--update_model', help='debug 或 release 模式', type=str, choices=['debug', 'release'], required=True)
    group_update = update_parser.add_mutually_exclusive_group(required=True)
    group_update.add_argument('-p', '--profile_path', help='mobileprovision 文件路径', type=str)
    group_update.add_argument('-i', '--identity_value', help='证书身份值', type=str)

    # 版本命令
    version_parser = subparsers.add_parser("version", help="显示版本信息")

    args = parser.parse_args()

    config = ConfigHandler()

    if args.command == "sign":
        signer = AppSigner(config)
        options = {
            'inject_dylibs': args.inject,
            'output_path': args.output,
            'release': args.release,
            'bundle_id': args.bundle_id,
            'bundle_name': args.bundle_name,
            'device_id': args.device_id,
            'print_info': args.info,
            'restore_symbol': args.symbol,
            'install': args.install
        }
        signer.run(args.sign, options)
    elif args.command == "update":
        updater = EUpdate(config)
        if args.profile_path:
            updater.update_mobileprovision(args.profile_path, args.update_model)
        elif args.identity_value:
            updater.update_identity(args.identity_value, args.update_model)
    elif args.command == "version":
        print(f"ESign 版本: {__version__}")

if __name__ == "__main__":
    main()