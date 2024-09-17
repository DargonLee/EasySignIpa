import json
import os
import plistlib
import subprocess
from esign.elogger import Logger

class AppInfoManager:
    def __init__(self, info_plist_file_path: str):
        self.info_plist_file_path = info_plist_file_path
        info_plist_dir = os.path.dirname(self.info_plist_file_path)
        self.plugins_dir = os.path.join(info_plist_dir, 'PlugIns')
        self.extensions_dir = os.path.join(info_plist_dir, 'Extensions')
        self.logger = Logger()

    def print_info_plist_content(self):
        self.logger.info(self.logger.green("✅ app info plist content"))
        try:
            with open(self.info_plist_file_path, 'rb') as f:
                plist_content = plistlib.load(f)
                json_content = json.dumps(plist_content, indent=4, ensure_ascii=False)
                print(json_content)
        except Exception as e:
            self.logger.error(f"读取 Info.plist 失败: {str(e)}")

    def print_app_info(self):
        self.logger.info(self.logger.green("✅ app base info"))
        try:
            bundle_name = self._get_plist_value("CFBundleName")
            bundle_id = self._get_plist_value("CFBundleIdentifier")
            short_version = self._get_plist_value("CFBundleShortVersionString")
            executable_name = self._get_plist_value("CFBundleExecutable")

            print(f"[*] BundleName: {bundle_name}")
            print(f"[*] BundleID: {bundle_id}")
            print(f"[*] ShortVersion: {short_version}")
            print(f"[*] ExecutableName: {executable_name}")
        except Exception as e:
            self.logger.error(f"获取应用信息失败: {str(e)}")

    def modify_bundle_id(self, new_bundle_id: str):
        self.logger.info(self.logger.green("✅ 修改 Bundle ID"))
        try:
            # 修改 Info.plist 中的 Bundle ID
            self._set_plist_value("CFBundleIdentifier", new_bundle_id)
            # 同步修改插件中的包名
            self._update_plugin_bundle_id(new_bundle_id)
            self.logger.info(f"[*] Bundle ID 修改成功: {new_bundle_id}")
        except Exception as e:
            self.logger.error(f"修改 Bundle ID 失败: {str(e)}")

    def modify_bundle_name(self, new_bundle_name: str):
        self.logger.info(self.logger.green("✅ 修改 Bundle Name"))
        try:
            # 修改 Info.plist 中的 Bundle Name
            self._set_plist_value("CFBundleName", new_bundle_name)
            self.logger.info(f"[*] Bundle Name 修改成功: {new_bundle_name}")
        except Exception as e:
            self.logger.error(f"修改 Bundle Name 失败: {str(e)}")

    def _set_plist_value(self, key: str, value: str):
        cmd = f'/usr/libexec/PlistBuddy -c "Set :{key} {value}" {self.info_plist_file_path}'
        subprocess.getoutput(cmd)

    def _update_plugin_bundle_id(self, new_bundle_id: str):
        # 处理插件和扩展
        for directory in [self.plugins_dir, self.extensions_dir]:
            if not os.path.exists(directory):
                print(f"[-]No {os.path.basename(directory)} directory found")
                continue
            
            # 遍历目录
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if not item_path.endswith('.appex'):
                    continue
                
                item_info_plist = os.path.join(item_path, "Info.plist")
                if not os.path.exists(item_info_plist):
                    print(f"[-]Info.plist for {item} does not exist")
                    continue
                
                # 获取原始包名
                ori_item_bundle_id = subprocess.getoutput(
                    f'/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "{item_info_plist}"'
                ).strip()

                # 获取原始包名的最后一个部分
                item_suffix = ori_item_bundle_id.split('.')[-1]
                print(f"[-]Suffix for {item}: {item_suffix}")

                # 构造新的包名
                new_item_bundle_id = f"{new_bundle_id}.{item_suffix}"
                
                # 修改包名
                subprocess.getoutput(
                    f'/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {new_item_bundle_id}" "{item_info_plist}"'
                )
                print(f"[-]Bundle ID for {item} modified: {ori_item_bundle_id} => {new_item_bundle_id}")


    def _get_plist_value(self, key: str) -> str:
        cmd = f'/usr/libexec/PlistBuddy -c "Print :{key}" {self.info_plist_file_path}'
        return subprocess.getoutput(cmd).strip()