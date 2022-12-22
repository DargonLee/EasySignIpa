# class Color:
#     Black = 0
#     Red = 1
#     Green = 2
#     Yellow = 3
#     Blue = 4
#     Magenta = 5
#     Cyan = 6
#     White = 7
#
#
# class Mode:
#     Foreground = 30
#     Background = 40
#     ForegroundBright = 90
#     BackgroundBright = 100
#
#
# def tcolor(c, m=Mode.Foreground):
#     return "\033[{}m".format(m + c)
#
#
# def treset():
#     return "\033[0m"

class Logger:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    CYAN = "\033[36m"
    END = "\033[0m"
    def __init__(self):
        print("init tool")
    def cyan(msg):
        print(Logger.CYAN + msg + Logger.END)
    def blue(msg):
        print(Logger.BLUE + msg + Logger.END)
    def white(msg):
        print(Logger.WHITE + msg + Logger.END)
    @staticmethod
    def red(msg):
        print(Logger.RED + msg + Logger.END)
    @staticmethod
    def green(msg):
        print(Logger.GREEN + msg + Logger.END)
    @staticmethod
    def yellow(msg):
        print(Logger.YELLOW + msg + Logger.END)

    @staticmethod
    def info(msg):
        print(Logger.WHITE + msg + Logger.END)

    @staticmethod
    def warning(msg):
        print(Logger.YELLOW + msg + Logger.END)

    @staticmethod
    def error(msg):
        print(Logger.RED + msg + Logger.END)


# end if Logger ------------------------------

# -------------------------------------------------------------
# class ZFile:
#     """
#     文件压缩
#     """
#
#     @staticmethod
#     def writInto(zipObj, fromddr, basePathName):
#         if os.path.isfile(fromddr):
#             zipObj.write(fromddr, fromddr.replace(basePathName))
#         else:
#             files = os.listdir(fromddr)
#             for fileObj in files:
#                 if os.path.isfile(fromddr + os.sep + fileObj):
#                     path = fromddr + os.sep + fileObj
#                     archName = path.replace(basePathName + os.sep, "")
#                     print(fromddr + os.sep + fileObj, archName)
#                     zipObj.write(fromddr + os.sep + fileObj, arcname=archName)
#                 else:
#                     ZFile.writInto(zipObj, fromddr + os.sep + fileObj, basePathName)
#
#     @staticmethod
#     def zip_file(fromddr, toAddr):
#         zipObj = zipfile.ZipFile(toAddr, mode="a")
#         if os.path.isfile(fromddr):
#             basePathName = os.path.split(fromddr)[0]
#             ZFile.writInto(zipObj, fromddr, basePathName)
#             zipObj.close()
#         else:
#             ZFile.writInto(zipObj, fromddr, fromddr)
#             zipObj.close()
#
#     @staticmethod
#     def unzip_file(fz_name, path):
#         """
#         解压缩文件
#         :param fz_name: zip文件
#         :param path: 解压缩路径
#         :return:
#         """
#         flag = False
#
#         if zipfile.is_zipfile(fz_name):  # 检查是否为zip文件
#             with zipfile.ZipFile(fz_name, "r") as zipf:
#                 zipf.extractall(path)
#                 # for p in zipf.namelist():
#                 #     # 使用cp437对文件名进行解码还原， win下一般使用的是gbk编码
#                 #     p = p.encode('cp437').decode('gbk')  # 解决中文乱码
#                 #     print(fz_name, p,path)
#                 flag = True
#
#         return {"file_name": fz_name, "flag": flag}


# end if unzip ------------------------------

# if __name__ == "__main__":
#     print(Logger.red("I am red! {}".format(["Lee", "Lee1"])))
#     print(Logger.green("I am green!"))
#     print(Logger.yellow("I am yellow!"))
#     print(Logger.blue("I am blue!"))
#     # print(Logger.magenta("I am magenta!"))
#     print(Logger.cyan("I am cyan!"))
#     print(Logger.white("I am white!"))
#     # print(Logger.white_green("I am white green!"))