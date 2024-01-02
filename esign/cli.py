import sys
import argparse
from esign import ESigner
import os


def parse_prompt_arg(prompt_arg):
    prompt = None

    print("prompt config:", prompt)
    return prompt


def main():
    parser = argparse.ArgumentParser(description="ipa re-signature command tool")
    parser.add_argument(
        "-c", "--config", help="config signing cert and provision", action="store_true"
    )
    parser.add_argument("-s", "--sign", help="re-signing the .ipa or .app", type=str)
    parser.add_argument(
        "-l", "--inject", help="injecting dynamic library into the app", type=str
    )
    parser.add_argument("-o", "--output", help="output the resigned ipa", type=str)

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        "-b",
        "--install",
        help="install the re-signed ipa onto the device connected via USB.",
        action="store_true",
    )
    group.add_argument(
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

    esign_obj = ESigner()
    if args.sign:
        if esign_obj.check_run_env() == False:
            print(f"Error: {esign_obj.identity} does not Correspondence with {esign_obj.mobileprovision}.")
            exit(1)

        app_path = os.path.abspath(args.sign)
        esign_obj.resign(app_path, args.inject, output_path, install_type)

    if args.config:
        if esign_obj.set_run_env() == False:
            print(f"Error: {esign_obj.identity} does not Correspondence with {esign_obj.mobileprovision}.")
            exit(1)
        else:
            print("Success: config signing cert and provision.")


if __name__ == "__main__":
    main()
