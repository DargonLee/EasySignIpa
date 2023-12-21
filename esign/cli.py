import sys
import argparse
from esign import esign

version = "v2.0.0"


def parse_prompt_arg(prompt_arg):
    prompt = None

    print("prompt config:", prompt)
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="ipa re-signature command tool {}".format(version)
    )
    parser.add_argument("-v", "--version", help="esign version", action="store_true")
    parser.add_argument("-s", "--sign", help="re-signing the ipa", type=str)
    parser.add_argument(
        "-l", "--inject", help="injecting dynamic library into the app", type=str
    )
    parser.add_argument("-o", "--output", help="output the resigned ipa", type=str)
    parser.add_argument(
        "-b",
        "--install",
        help="install the re-signed ipa onto the device connected via USB,exclusive with the -rb command.",
        type=str,
    )
    parser.add_argument(
        "-rb",
        "--reinstall",
        help="uninstall the app with the same package name on the device first, and then install the re-signed app,exclusive with the -b command.",
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

    if args.version:
        print(version)

    if args.sign:
        dylibs = []
        if args.vss:
            dylibs.append("Vss")
        esign.do_resign(
            args.sign, args.release, args.reinstall, dylibs, args.create_ipa
        )

    if args.listapp:
        esign.listApplicationDir(args.listapp)


if __name__ == "__main__":
    main()
