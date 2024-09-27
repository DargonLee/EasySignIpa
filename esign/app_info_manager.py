import asyncio
import json
import os
import plistlib
import subprocess
from esign.elogger import Logger
from esign.exceptions import AppInfoManagerError

class AppInfoManager:
    def __init__(self, prepared_app_path: str):
        self.info_plist_file_path = os.path.join(prepared_app_path, 'Info.plist')
        if not os.path.exists(self.info_plist_file_path):
            raise AppInfoManagerError("Info.plist path does not exist")

        info_plist_dir = os.path.dirname(self.info_plist_file_path)
        self.plugins_dir = os.path.join(info_plist_dir, 'PlugIns')
        self.extensions_dir = os.path.join(info_plist_dir, 'Extensions')
        self.logger = Logger()

    def print_info_plist_content(self):
        self.logger.info("App info plist content")
        try:
            with open(self.info_plist_file_path, 'rb') as f:
                plist_content = plistlib.load(f)
                json_content = json.dumps(plist_content, indent=4, ensure_ascii=False)
                print(json_content)
        except Exception as e:
            self.logger.error(f"Fail to read Info.plist: {str(e)}")

    def print_app_info(self):
        self.logger.info("App info")
        try:
            bundle_info = {
                "BundleName": self.get_bundle_name(),
                "BundleID": self.get_bundle_id(),
                "ShortVersion": self.get_short_version(),
                "ExecutableName": self.get_executable_name(),
                "BundleVersion": self.get_bundle_version()
            }
            for key, value in bundle_info.items():
                self.logger.default(f"{key}: {value}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve application information: {str(e)}")
    
    def modify_bundle_id(self, new_bundle_id: str):
        try:
            self.logger.info(f"Modifying Bundle ID:")
            oldBundleId = self._get_plist_value(self.info_plist_file_path, "CFBundleIdentifier")
            self._set_plist_value(self.info_plist_file_path,"CFBundleIdentifier", new_bundle_id)
            self._update_plugin_bundle_id(new_bundle_id)
            self.logger.default(f"{oldBundleId} to {new_bundle_id}")
        except Exception as e:
            self.logger.error(f"Modifying Bundle ID fail: {str(e)}")

    def modify_bundle_name(self, new_bundle_name: str):
        try:
            self.logger.info(f"Modifying Bundle Name:")
            oldBundleName = self._get_plist_value(self.info_plist_file_path, "CFBundleName")
            self._set_plist_value(self.info_plist_file_path,"CFBundleName", new_bundle_name)
            self.logger.default(f"{oldBundleName} to {new_bundle_name}")
        except Exception as e:
            self.logger.error(f"Failed to modify Bundle Name: {str(e)}")

    def delete_support_devices(self):
        self._delete_item_value(self.info_plist_file_path, "UISupportedDevices")

    def get_executable_name(self) -> str:
        executable_name = self._get_plist_value(self.info_plist_file_path, "CFBundleExecutable")
        return executable_name

    def get_bundle_name(self) -> str:
        bundle_name = self._get_plist_value(self.info_plist_file_path, "CFBundleName")
        return bundle_name

    def get_bundle_id(self) -> str:
        bundle_id = self._get_plist_value(self.info_plist_file_path, "CFBundleIdentifier")
        return bundle_id

    def get_short_version(self) -> str:
        short_version = self._get_plist_value(self.info_plist_file_path, "CFBundleShortVersionString")
        return short_version

    def get_bundle_version(self) -> str:
        bundle_version = self._get_plist_value(self.info_plist_file_path, "CFBundleVersion")
        return bundle_version

    def _update_plugin_bundle_id(self, new_bundle_id: str):

        for directory in [self.plugins_dir, self.extensions_dir]:
            if not os.path.exists(directory):
                self.logger.warning(f"No {os.path.basename(directory)} directory found")
                continue

            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if not item_path.endswith('.appex'):
                    continue

                item_info_plist = os.path.join(item_path, "Info.plist")
                if not os.path.exists(item_info_plist):
                    self.logger.error(f"Info.plist for {item} does not exist")
                    continue

                ori_item_bundle_id = self._get_plist_value(item_info_plist, "CFBundleIdentifier")
                if not ori_item_bundle_id:
                    continue

                item_suffix = ori_item_bundle_id.split('.')[-1]
                self.logger.info(f"Suffix for {item}: {item_suffix}")
                new_item_bundle_id = f"{new_bundle_id}.{item_suffix}"
                if self._set_plist_value(item_info_plist, "CFBundleIdentifier", new_item_bundle_id):
                    self.logger.default(f"Bundle ID for {item} modified: {ori_item_bundle_id} => {new_item_bundle_id}")
                else:
                    self.logger.error(f"Failed to modify bundle ID for {item}")
                    
    def _set_plist_value(self, plist_path: str, key: str, value: str):
        cmd = f'/usr/libexec/PlistBuddy -c "Set :{key} {value}" {plist_path}'
        result = subprocess.getoutput(cmd).strip()
        self.logger.default(f"success modify info.plist: {key} => {value}")

    def _get_plist_value(self, plist_path: str, key: str) -> str:
        cmd = f'/usr/libexec/PlistBuddy -c "Print :{key}" {plist_path}'
        return subprocess.getoutput(cmd).strip()
    
    def _delete_item_value(self, plist_path: str, key: str):
        cmd = f'/usr/libexec/PlistBuddy -c "Delete :{key}" {plist_path}'
        subprocess.getoutput(cmd).strip()