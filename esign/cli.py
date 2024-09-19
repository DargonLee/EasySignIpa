import argparse
from esign.app_signer import AppSigner
from esign.econfig import ConfigHandler
from esign.eupdate import EUpdate
from esign import __version__

def main():
    parser = argparse.ArgumentParser(description="IPA Resigning Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sign command
    sign_parser = subparsers.add_parser("sign", help="Resign an IPA or APP")
    sign_parser.add_argument('-f', '--file', help='Path to the .ipa or .app file to be resigned', type=str, required=True)
    sign_parser.add_argument('-l', '--inject', help='Path to the dynamic library to inject', type=str, action='append')
    sign_parser.add_argument('-o', '--output', help='Path to the output resigned IPA file: path/to/output.ipa', type=str)
    sign_parser.add_argument('-r', '--release', help='Use the release certificate for signing', action='store_true')
    sign_parser.add_argument('--bundle_id', help='Modify the application bundle ID', type=str)
    sign_parser.add_argument('--bundle_name', help='Modify the application display name', type=str)
    sign_parser.add_argument('--info', help='Print the contents of Info.plist', action='store_true')
    sign_parser.add_argument('--symbol', help='Restore symbol table', action='store_true')
    sign_parser.add_argument('--clear_plugins', help='Clear the plugins folder', action='store_true', default=True)

    # Installation options
    sign_parser.add_argument('-d', '--device_id', help='Specify the installation device ID', type=str)
    group_install = sign_parser.add_mutually_exclusive_group(required=True)
    group_install.add_argument('-b', '--install', help='Install the resigned IPA or APP', action='store_true')
    group_install.add_argument('-rb', '--reinstall', help='Uninstall the existing app with the same name before installing', action='store_true')

    # Update command
    update_parser = subparsers.add_parser("update", help="Update signing configurations")
    update_parser.add_argument('-m', '--update_model', help='Specify either debug or release mode', type=str, choices=['debug', 'release'], required=True)
    group_update = update_parser.add_mutually_exclusive_group(required=True)
    group_update.add_argument('-p', '--profile_path', help='Path to the mobileprovision file', type=str)
    group_update.add_argument('-i', '--identity_value', help='Certificate identity value', type=str)

    # Version command
    version_parser = subparsers.add_parser("version", help="Display version information")

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
            'install': args.install,
            'reinstall': args.reinstall,
            'clear_plugins': args.clear_plugins,
        }
        signer.run(args.file, options)
    elif args.command == "update":
        updater = EUpdate(config)
        if args.profile_path:
            updater.update_mobileprovision(args.profile_path, args.update_model)
        elif args.identity_value:
            updater.update_identity(args.identity_value, args.update_model)
    elif args.command == "version":
        print(f"ESign version: {__version__}")

if __name__ == "__main__":
    main()