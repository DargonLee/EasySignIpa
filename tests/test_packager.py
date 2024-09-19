import os
import unittest
import asyncio
from esign.econfig import ConfigHandler
from esign.exceptions import IPAPackagingError
from esign.ipa_packager import IPAPackager

class TestIPAPackager(unittest.TestCase):

    def setUp(self):
        self.config = ConfigHandler()
        self.packager = IPAPackager(self.config)

    def test_create_ipa_success(self):
        """测试打包成功的情况"""
        payload_path = "/Users/apple/Downloads/Payload/DumpApp.app"
        output_path = "/Users/apple/Downloads/Payload/output.ipa"

        # 使用 asyncio 来运行异步函数
        asyncio.run(self.packager.package(payload_path, output_path))

        # 检查 IPA 文件是否创建
        self.assertTrue(os.path.exists(output_path))

    def test_create_ipa_no_payload(self):
        """测试当 payload 路径不存在时的情况"""
        payload_path = "/path/to/invalid/Payload/YourApp.app"
        output_path = "/path/to/output/output.ipa"

        with self.assertRaises(IPAPackagingError):
            asyncio.run(self.packager.package(payload_path, output_path))

    def test_create_ipa_permission_error(self):
        """测试当输出路径没有写权限时的情况"""
        payload_path = "/path/to/valid/Payload/YourApp.app"
        output_path = "/protected/output.ipa"  # 无写权限目录

        with self.assertRaises(IPAPackagingError):
            asyncio.run(self.packager.package(payload_path, output_path))

    def tearDown(self):
        """清理输出文件"""
        output_path = "/path/to/output/output.ipa"
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    unittest.main()
