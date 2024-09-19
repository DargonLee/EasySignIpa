import os
import zipfile
import asyncio
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import IPAPackagingError

class IPAPackager:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def package(self, payload_path: str, output_path: str):
        self.logger.info("Starting packaging process")
        try:
            await self._create_ipa(payload_path, output_path)
            self.logger.default(f"IPA successfully packaged: {output_path}")
        except FileNotFoundError:
            self.logger.error(f"File not found: {payload_path}")
            raise IPAPackagingError(f"Packaging failed, file not found: {payload_path}")
        except PermissionError:
            self.logger.error(f"Permission denied: {output_path}")
            raise IPAPackagingError(f"Packaging failed, cannot write to: {output_path}")
        except Exception as e:
            raise IPAPackagingError(f"IPA packaging failed: {str(e)}")

    async def _create_ipa(self, payload_path: str, output_path: str):
        # 使用 asyncio 的 run_in_executor 来异步处理压缩任务
        await asyncio.to_thread(self._zip_payload, payload_path, output_path)
    def _zip_payload(self, payload_path: str, output_path: str):
        """
        压缩 payload_path 目录到 output_path 指定的 .ipa 文件中，
        使得压缩后的文件夹结构为 xxx.ipa/Payload/DumpApp.app。

        :param payload_path: 要压缩的目录路径，例如 'path/Payload/DumpApp.app'
        :param output_path: 输出的 .ipa 文件路径，例如 'output.ipa'
        """
        # 确定压缩文件的路径
        base_name = os.path.basename(output_path)
        if not base_name.endswith('.ipa'):
            raise ValueError("Output file path must end with .ipa")

        # 计算相对路径
        parent_dir = os.path.dirname(payload_path)
        payload_name = os.path.basename(payload_path)

        # 打开压缩文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(payload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算文件在压缩包中的相对路径
                    # 'Payload/DumpApp.app' 应该是根目录下的路径
                    arcname = os.path.relpath(file_path, parent_dir)
                    arcname = os.path.join('Payload', payload_name, arcname)
                    zipf.write(file_path, arcname)

