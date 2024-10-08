class ESignError(Exception):
    """ESign 工具的基础异常类"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ConfigError(ESignError):
    """配置相关的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class AppPreparationError(ESignError):
    """应用准备过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class CodeSigningError(ESignError):
    """代码签名过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class DylibInjectionError(ESignError):
    """动态库注入过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class EntitlementsError(ESignError):
    """权限文件处理过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class IPAPackagingError(ESignError):
    """IPA 打包过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class ProvisioningProfileError(ESignError):
    """配置文件处理过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class SymbolRestorationError(ESignError):
    """符号表恢复过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class AppInstallationError(ESignError):
    """应用安装过程中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class EncryptionCheckError(ESignError):
    """检查可执行文件中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")

class AppInfoManagerError(ESignError):
    """AppInfoManager 中的异常"""
    def __init__(self, message: str):
        super().__init__(f"{message}")