import os
import zipfile
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import IPAPackagingError

class IPAPackager:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()

    async def package(self, payload_path: str, output_path: str):
        try:
            self._create_ipa(payload_path, output_path)
            self.logger.info(f"IPA 打包成功: {output_path}")
        except Exception as e:
            raise IPAPackagingError(f"IPA 打包失败: {str(e)}")

    def _create_ipa(self, payload_path: str, output_path: str):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(payload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(payload_path))
                    zipf.write(file_path, arcname)