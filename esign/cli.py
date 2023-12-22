import sys
import argparse
import esign
import econfig

import site
print(site.getsitepackages())


def parse_prompt_arg(prompt_arg):
    prompt = None

    print("prompt config:", prompt)
    return prompt


def main():
    parser = argparse.ArgumentParser(description="ipa re-signature command tool")
    parser.add_argument("-c", "--config", help="config signing cert and provision", type=str)
    parser.add_argument("-s", "--sign", help="re-signing the ipa", type=str)
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

    # command.check_run_env(args)
    # while not command.check_run_env(args):
    #     pass
    # exit(0)

    if len(sys.argv) == 1:
        parser.print_help()

    # print(args);
    # print(sys.argv[1])

    if args.install:
        print("Option B selected")
    elif args.reinstall:
        print("Option RB selected")

    if args.sign:
        dylibs = []
        if args.inject:
            dylibs.append(args.inject)
        esign.do_resign(
            args.sign, args.release, args.reinstall, dylibs, args.create_ipa
        )

    if args.config:
        econfig.do_config(args.config)


if __name__ == "__main__":
    main()
