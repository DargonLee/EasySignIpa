import os
import zipfile


class EZipFile:
    """
    文件压缩
    """

    @staticmethod
    def _writInto(zipObj, fromddr, basePathName):
        if os.path.isfile(fromddr):
            zipObj.write(fromddr, fromddr.replace(basePathName))
        else:
            files = os.listdir(fromddr)
            for fileObj in files:
                if os.path.isfile(fromddr + os.sep + fileObj):
                    path = fromddr + os.sep + fileObj
                    archName = path.replace(basePathName + os.sep, "")
                    print(fromddr + os.sep + fileObj, archName)
                    zipObj.write(fromddr + os.sep + fileObj, arcname=archName)
                else:
                    EZipFile.writInto(zipObj, fromddr + os.sep + fileObj, basePathName)

    @staticmethod
    def zip_file(fromddr, toAddr):
        """
        压缩指定文件夹
        :param dir_path: 要压缩的文件夹路径
        :param zip_path: 压缩文件保存路径
        """
        zipObj = zipfile.ZipFile(toAddr, mode="a")
        if os.path.isfile(fromddr):
            basePathName = os.path.split(fromddr)[0]
            EZipFile._writInto(zipObj, fromddr, basePathName)
            zipObj.close()
        else:
            EZipFile.writInto(zipObj, fromddr, fromddr)
            zipObj.close()

    @staticmethod
    def unzip_file(fz_name, path):
        """
        解压缩文件
        :param fz_name: zip文件
        :param path: 解压缩路径
        :return:
        """
        flag = False

        if zipfile.is_zipfile(fz_name):  # 检查是否为zip文件
            with zipfile.ZipFile(fz_name, "r") as zipf:
                zipf.extractall(path)
                flag = True

        return {"file_name": fz_name, "flag": flag}


if __name__ == "__main__":
    print(EZipFile.zip_file("/User/Lee/Desktop/1", "/User/Lee/Desktop/1.zip"))
