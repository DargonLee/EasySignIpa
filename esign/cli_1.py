import sys
import argparse
from esign.esign import ESigner
from esign.eupdate import EUpdate
import os


def parse_prompt_arg(prompt_arg):
    prompt = None

    print("prompt config:", prompt)
    return prompt


def get_version():
    return "0.9.5"


def main():
    parser = argparse.ArgumentParser(description="ipa re-signature command tool")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {get_version()}',
                        help='show version and exit'
                        )
    parser.add_argument("-s", "--sign", help="re-signing the .ipa or .app", type=str)
    parser.add_argument(
        "-l", "--inject", help="injecting dynamic library into the app", type=str
    )
    parser.add_argument("-o", "--output", help="output the resigned ipa", type=str)
    parser.add_argument("-r", "--release", help="sign release ipa", action="store_true")

    parser.add_argument("--bundle_id", help="modify app bundle id value", type=str)
    parser.add_argument("--bundle_name", help="modify app bundle display name", type=str)
    parser.add_argument("--device_id", help="designated device installation", type=str)
    parser.add_argument("--info", help="print Info.plist content", action="store_true")
    parser.add_argument("--symbol", help="restore_symbol", action="store_true")

    update_subparsers = parser.add_subparsers(dest="command")
    update_provision_parser = update_subparsers.add_parser('update', help='update resign mobileprovision')
    group_update = update_provision_parser.add_mutually_exclusive_group(required=False)
    group_update.add_argument("-p", "--profile_path",
                        help="please provide the path to the mobileprovision file",
                        type=str)
    group_update.add_argument("-i", "--identity_value", help="please provide the identity value",
                        type=str)
    update_provision_parser.add_argument("-m", "--update_model",
                               help="debug or release mobileprovision file",
                               type=str, default="debug")

    group_install = parser.add_mutually_exclusive_group(required=False)
    group_install.add_argument(
        "-b",
        "--install",
        help="install the re-signed ipa onto the device connected via USB.",
        action="store_true",
    )
    group_install.add_argument(
        "-rb",
        "--reinstall",
        help="uninstall the app with the same package name on the device first, and then install the re-signed app.",
        action="store_true",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if args.command == "update":
        if args.profile_path:
            profile_path = os.path.abspath(args.profile_path)
            EUpdate.update_mobileprovision(profile_path, args.update_model)
        elif args.identity_value:
            identity_value = args.update_identity
            EUpdate.update_identity(identity_value, args.update_model)

    install_type = None
    if args.install:
        install_type = "b"
    elif args.reinstall:
        install_type = "rb"

    output_path = None
    if args.output:
        output_path = os.path.abspath(args.output)

    inject_dylib_list = []
    if args.inject:
        inject_dylib_path = os.path.abspath(args.inject)
        inject_dylib_list.append(inject_dylib_path)

    esign_obj = ESigner()
    if args.sign:
        app_path = os.path.abspath(args.sign)
        esign_obj.resign(app_path,
                         inject_dylib_list,
                         output_path,
                         install_type,
                         args.info,
                         args.bundle_id,
                         args.bundle_name,
                         args.release,
                         args.device_id,
                         args.symbol
                         )


if __name__ == "__main__":
    main()
