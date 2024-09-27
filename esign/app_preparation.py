import asyncio
import os
import shutil
import zipfile
from typing import Tuple
from esign.econfig import ConfigHandler
from esign.elogger import Logger
from esign.exceptions import AppPreparationError

class AppPreparation:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.no_clear_plugins = True
        self.logger = Logger()

    async def prepare(self, app_path: str, no_clear_plugins) -> Tuple[str, str]:

        self.no_clear_plugins = no_clear_plugins

        try:
            self.logger.info(f"Preparing: {app_path}")
            app_name, app_extension = os.path.splitext(os.path.basename(app_path))
            
            if not os.path.exists(app_path):
                raise AppPreparationError(f"File does not exist: {app_path}")

            if app_extension not in ['.ipa', '.app']:
                raise AppPreparationError(f"Unsupported file type: {app_extension}")

            if app_extension == '.ipa':
                return await self._prepare_ipa(app_path)
            else:
                return await self._prepare_app(app_path)
        except Exception as e:
            raise AppPreparationError(f"Preparing fail {str(e)}")

    async def _prepare_ipa(self, ipa_path: str) -> Tuple[str, str]:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        payload_path = os.path.join(temp_dir, 'Payload')
        app_path = next(os.path.join(payload_path, f) for f in os.listdir(payload_path) if f.endswith('.app'))
        
        await self._clean_app(app_path)
        return payload_path, app_path

    async def _prepare_app(self, app_path: str) -> Tuple[str, str]:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        payload_path = os.path.join(temp_dir, 'Payload')
        os.makedirs(payload_path, exist_ok=True)
        
        shutil.copytree(app_path, os.path.join(payload_path, os.path.basename(app_path)))
        await self._clean_app(os.path.join(payload_path, os.path.basename(app_path)))

        return payload_path, os.path.join(payload_path, os.path.basename(app_path))

    async def _clean_app(self, app_path: str):
        dirs_to_remove = ['SC_Info', 'Watch', '_CodeSignature', 'PlugIns', 'Extensions']
        files_to_remove = ['.DS_Store']

        if self.no_clear_plugins:
            dirs_to_remove.remove('PlugIns')
            dirs_to_remove.remove('Extensions')

        for dir_name in dirs_to_remove:
            dir_path = os.path.join(app_path, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                self.logger.default(f"Deleting: directory: {dir_name}")

        for file_name in files_to_remove:
            file_path = os.path.join(app_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.default(f"Deleting: file: {file_name}")