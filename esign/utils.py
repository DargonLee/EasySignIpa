import getpass
import os

user_name = getpass.getuser()
ESIGN_DIR_PATH = "/Users/" + user_name + "/.esign/"
PROVISIONS_DIR_PATH = os.path.join(ESIGN_DIR_PATH, "provisions")
SETTINGS_PATH = os.path.join(ESIGN_DIR_PATH, "config/settings.ini")
IOS_DEPLOY_NEW_PATH = os.path.join(ESIGN_DIR_PATH, "bin/ios-deploy_new")
IDEVICEINSTALLER_PATH = os.path.join(ESIGN_DIR_PATH, "bin/ideviceinstaller")
OPTOOL_PATH = os.path.join(ESIGN_DIR_PATH, "bin/optool")
ZSIGN_PATH = os.path.join(ESIGN_DIR_PATH, "bin/zsign")
RESTORE_SYMBOL_PATH = os.path.join(ESIGN_DIR_PATH, "bin/restore-symbol")
UN_SIGN_PATH = os.path.join(ESIGN_DIR_PATH, "bin/unsign")
EMBEDDED_ENTITLEMENTS = "entitlements.plist"
EMBEDDED_ORI_ENTITLEMENTS = "ori_entitlements.plist"
EMBEDDED_PRO_ENTITLEMENTS = "pro_entitlements.plist"
PROFILE_PLIST = "profile.plist"
