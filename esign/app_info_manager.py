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
        self.logger.info("app base info")
        try:
            bundle_info = {
                "BundleName": self._get_plist_value("CFBundleName"),
                "BundleID": self._get_plist_value("CFBundleIdentifier"),
                "ShortVersion": self._get_plist_value("CFBundleShortVersionString"),
                "ExecutableName": self._get_plist_value("CFBundleExecutable")
            }
            for key, value in bundle_info.items():
                self.logger.default(f"[*] {key}: {value}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve application information: {str(e)}")

    def modify_bundle_id(self, new_bundle_id: str):
        try:
            self._set_plist_value("CFBundleIdentifier", new_bundle_id)
            asyncio.run(self._update_plugin_bundle_id(new_bundle_id))
            self.logger.info(f"Modifying Bundle ID to: {new_bundle_id}")
        except Exception as e:
            self.logger.error(f"Modifying Bundle ID fail: {str(e)}")

    def modify_bundle_name(self, new_bundle_name: str):
        try:
            self._set_plist_value("CFBundleName", new_bundle_name)
            self.logger.info(f"Bundle Name successfully changed to: {new_bundle_name}")
        except Exception as e:
            self.logger.error(f"Failed to modify Bundle Name: {str(e)}")

    async def _update_plugin_bundle_id(self, new_bundle_id: str):

        for directory in [self.plugins_dir, self.extensions_dir]:
            if not os.path.exists(directory):
                self.logger.error(f"No {os.path.basename(directory)} directory found")
                continue

            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if not item_path.endswith('.appex'):
                    continue

                item_info_plist = os.path.join(item_path, "Info.plist")
                if not os.path.exists(item_info_plist):
                    self.logger.error(f"Info.plist for {item} does not exist")
                    continue

                ori_item_bundle_id = await self._get_bundle_id(item_info_plist)
                if not ori_item_bundle_id:
                    continue

                item_suffix = ori_item_bundle_id.split('.')[-1]
                self.logger.info(f"Suffix for {item}: {item_suffix}")

                new_item_bundle_id = f"{new_bundle_id}.{item_suffix}"

                if await self._set_bundle_id(item_info_plist, new_item_bundle_id):
                    self.logger.default(f"Bundle ID for {item} modified: {ori_item_bundle_id} => {new_item_bundle_id}")
                else:
                    self.logger.error(f"Failed to modify bundle ID for {item}")

    async def _get_bundle_id(self, plist_path):
        cmd = f'/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "{plist_path}"'
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            self.logger.error(f"Failed to get bundle ID from {plist_path}: {stderr.decode().strip()}")
            return None
        return stdout.decode().strip()

    async def _set_bundle_id(self, plist_path, new_bundle_id):
        cmd = f'/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {new_bundle_id}" "{plist_path}"'
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await process.communicate()
        if process.returncode != 0:
            self.logger.error(f"Failed to set bundle ID to {new_bundle_id} for {plist_path}")
            return False
        return True
 
    async def _set_plist_value(self, key: str, value: str):
        cmd = f'/usr/libexec/PlistBuddy -c "Set :{key} {value}" {self.info_plist_file_path}'
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Failed to set property value: {stderr.decode()}")

        self.logger.default(f"success modify info.plist: {key} => {value}")

    def _get_plist_value(self, key: str) -> str:
        cmd = f'/usr/libexec/PlistBuddy -c "Print :{key}" {self.info_plist_file_path}'
        return subprocess.getoutput(cmd).strip()
