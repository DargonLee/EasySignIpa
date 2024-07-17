import sys
import argparse
from esign.esign import ESigner
import os


def parse_prompt_arg(prompt_arg):
    prompt = None

    print("prompt config:", prompt)
    return prompt

def get_version():
    return "0.9.4"

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
    parser.add_argument("--info", help="print Info.plist content", action="store_true")

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
                         )

if __name__ == "__main__":
    main()
