import asyncio
import os
from typing import Dict
from esign.app_preparation import AppPreparation
from esign.code_signing import CodeSigning
from esign.econfig import ConfigHandler
from esign.dylib_injector import DylibInjector
from esign.entitlements_manager import EntitlementsManager
from esign.ipa_packager import IPAPackager
from esign.elogger import Logger
from esign.exceptions import ESignError
from esign.app_info_manager import AppInfoManager
from esign.app_installer import AppInstaller
from esign.symbol_restorer import SymbolRestorer
from esign.encryption_checker import EncryptionChecker

class AppSigner:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self.logger = Logger()
        self.app_preparer = AppPreparation(config)
        self.code_signer = CodeSigning(config)
        self.dylib_injector = DylibInjector(config)
        self.entitlements_manager = EntitlementsManager(config)
        self.ipa_packager = IPAPackager(config)
        self.app_installer = AppInstaller(config)
        self.symbol_restorer = SymbolRestorer(config)
        self.encryption_checker = EncryptionChecker(config)

    async def resign(self, app_path: str, options: Dict[str, any]):
        try:
            payload_path, prepared_app_path = await self.app_preparer.prepare(app_path)
            
            info_plist_path = os.path.join(prepared_app_path, 'Info.plist')
            app_info_printer = AppInfoManager(info_plist_path)

            executable_name = app_info_printer._get_plist_value("CFBundleExecutable")
            executable_path = os.path.join(prepared_app_path, executable_name)

            # 检查主应用可执行文件是否加密
            is_encrypted = await self.encryption_checker.check_encryption(executable_path, prepared_app_path)
            if is_encrypted:
                raise ESignError("主应用可执行文件已加密，无法重签名")

            if options.get('bundle_id'):
                app_info_printer.modify_bundle_id(options['bundle_id'])

            if options.get('bundle_name'):
                app_info_printer.modify_bundle_name(options['bundle_name'])

            if options.get('inject_dylibs'):
                await self.dylib_injector.inject(prepared_app_path, options['inject_dylibs'])
                 
            if options.get('restore_symbol'):
                await self.symbol_restorer.restore(executable_path)

            identity = self.config.get_release_identity() if options.get('release') else self.config.get_debug_identity()
            provisioning_profile = self.config.get_release_mobileprovision_path() if options.get('release') else self.config.get_debug_mobileprovision_path()
            
            entitlements = await self.entitlements_manager.process(prepared_app_path, provisioning_profile)
            
            await self.code_signer.sign_all(prepared_app_path, identity, entitlements)
            
            if options.get('output_path'):
                await self.ipa_packager.package(payload_path, options['output_path'])

            if options.get('print_info'):
                app_info_printer.print_info_plist_content()
            
            app_info_printer.print_app_info()

            if options.get('install'):
                await self.app_installer.install(prepared_app_path, options.get('install'), options.get('device_id'))
            
            self.logger.info("重签名过程成功完成")
        except ESignError as e:
            self.logger.error(f"重签名失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"发生未知错误: {str(e)}")

    def run(self, app_path: str, options: Dict[str, any]):
        asyncio.run(self.resign(app_path, options))