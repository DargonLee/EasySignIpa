import subprocess
import unittest
from unittest.mock import patch, mock_open, MagicMock
import asyncio
import os
from esign.exceptions import AppInfoManagerError
from esign.app_info_manager import AppInfoManager


class TestAppInfoManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # 创建测试环境
        self.test_path = '/Users/apple/Downloads/Payload/DumpApp.app'
        self.info_plist_path = os.path.join(self.test_path, 'Info.plist')
        self.manager = AppInfoManager(self.test_path)

    @patch('os.path.exists')
    def test_init_info_plist_not_exists(self, mock_exists):
        mock_exists.side_effect = lambda path: path == self.info_plist_path

        with self.assertRaises(AppInfoManagerError):
            AppInfoManager(self.test_path)

    @patch('builtins.open', new_callable=mock_open, read_data='{"CFBundleName": "TestApp"}')
    @patch('plistlib.load', return_value={"CFBundleName": "TestApp"})
    @patch('json.dumps')
    def test_print_info_plist_content(self, mock_json_dumps, mock_plist_load, mock_open):
        mock_json_dumps.return_value = '{"CFBundleName": "TestApp"}'
        with patch('builtins.print') as mock_print:
            self.manager.print_info_plist_content()
            mock_print.assert_called_with('{"CFBundleName": "TestApp"}')

    @patch('app_info_manager.AppInfoManager._get_plist_value', return_value='TestValue')
    @patch('app_info_manager.Logger.info')
    def test_print_app_info(self, mock_logger_info, mock_get_plist_value):
        self.manager.print_app_info()
        calls = [
            unittest.mock.call("[*] BundleName: TestValue"),
            unittest.mock.call("[*] BundleID: TestValue"),
            unittest.mock.call("[*] ShortVersion: TestValue"),
            unittest.mock.call("[*] ExecutableName: TestValue")
        ]
        mock_logger_info.assert_has_calls(calls)

    @patch('app_info_manager.AppInfoManager._set_plist_value')
    @patch('app_info_manager.AppInfoManager._update_plugin_bundle_id')
    @patch('app_info_manager.Logger.info')
    def test_modify_bundle_id(self, mock_logger_info, mock_update_plugin, mock_set_plist_value):
        mock_set_plist_value.return_value = None
        mock_update_plugin.return_value = asyncio.Future()
        mock_update_plugin.return_value.set_result(None)

        self.manager.modify_bundle_id('com.new.bundle.id')
        mock_set_plist_value.assert_called_once_with('CFBundleIdentifier', 'com.new.bundle.id')
        mock_update_plugin.assert_called_once_with('com.new.bundle.id')
        mock_logger_info.assert_called_with("[*] Bundle ID 修改成功: com.new.bundle.id")

    @patch('app_info_manager.AppInfoManager._set_plist_value')
    @patch('app_info_manager.Logger.info')
    def test_modify_bundle_name(self, mock_logger_info, mock_set_plist_value):
        mock_set_plist_value.return_value = None

        self.manager.modify_bundle_name('NewAppName')
        mock_set_plist_value.assert_called_once_with('CFBundleName', 'NewAppName')
        mock_logger_info.assert_called_with("[*] Bundle Name 修改成功: NewAppName")

    @patch('app_info_manager.subprocess.getoutput', return_value='com.old.bundle.id')
    @patch('app_info_manager.asyncio.create_subprocess_shell')
    @patch('app_info_manager.Logger.info')
    async def test_update_plugin_bundle_id(self, mock_logger_info, mock_create_subprocess_shell,
                                           mock_subprocess_getoutput):
        mock_subprocess_getoutput.return_value = 'com.old.bundle.id'

        # Mock the behavior of subprocess for getting and setting bundle ID
        mock_get_process = MagicMock()
        mock_get_process.communicate.return_value = (b'com.old.bundle.id', b'')
        mock_get_process.returncode = 0
        mock_create_subprocess_shell.return_value = mock_get_process

        mock_set_process = MagicMock()
        mock_set_process.communicate.return_value = (b'', b'')
        mock_set_process.returncode = 0
        mock_create_subprocess_shell.return_value = mock_set_process

        # Run the async method
        await self.manager._update_plugin_bundle_id('com.new.bundle.id')

        # Validate if the commands were called correctly
        self.assertTrue(mock_create_subprocess_shell.called)
        mock_create_subprocess_shell.assert_any_call(
            '/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "/mock/path/to/app/PlugIns/sample.appex/Info.plist"',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_create_subprocess_shell.assert_any_call(
            '/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.new.bundle.id.sample" "/mock/path/to/app/PlugIns/sample.appex/Info.plist"',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_logger_info.assert_any_call("[-]Suffix for sample: sample")
        mock_logger_info.assert_any_call(
            "[-]Bundle ID for sample modified: com.old.bundle.id => com.new.bundle.id.sample")


if __name__ == '__main__':
    unittest.main()
