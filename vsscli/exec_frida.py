import threading
import frida
import codecs
import os
from vsscli.exec_tool import Logger

# 根目录
root_dir = os.path.dirname(os.path.realpath(__file__))
# js脚本目录
script_dir = os.path.join(root_dir, "js/")
# App.js文件
APP_JS = os.path.join(script_dir, "app.js")


# 获取第一个USB连接的设备
def get_usb_iphone():
    dManger = frida.get_device_manager()
    changed = threading.Event()

    def on_changed():
        changed.set()

    dManger.on("changed", on_changed)
    device = None
    while device is None:
        print(dManger.enumerate_devices())
        devices = [dev for dev in dManger.enumerate_devices() if dev.type == "usb"]
        if len(devices) == 0:
            print("✅ Writing for USB device...")
            changed.wait()
        else:
            # print("✅ 设备列表：\n{}".format(dManger.enumerate_devices()))
            device = devices[0]
    dManger.off("changed", on_changed)
    return device


# 列举手机的进程信息
def list_runing_process():
    device = frida.get_usb_device()
    processes = device.enumerate_processes()
    processes.sort(key=lambda item: item.pid)
    for process in processes:
        print("%-10s\t%s" % (str(process.pid), process.name))


# 加载js文件
def _load_js_file(session, filename):
    source = ""
    with codecs.open(filename, "r", "utf-8") as f:
        source = source + f.read()
    script = session.create_script(source)
    # script.on('message', on_message)
    script.load()
    return script


def listApplicationDir(args):
    device = frida.get_usb_device()
    print("✅ 设备信息：\n{}\n".format(device))

    print("✅ 应用安装信息：\n")
    session = device.attach("SpringBoard")
    script = _load_js_file(session, APP_JS)
    apps = script.exports.installed()
    for index in range(len(apps)):
        item = apps[index]
        data_path = "-"
        if len(item["dataPath"]):
            data_path = item["dataPath"]
        vsa_path = item["vsaPath"]
        if vsa_path == "true":
            vsa_path = "沙箱App"
        else:
            vsa_path = ""
        print(
            "#{}【{}】<{}> {}".format(
                Logger.white("{}".format(index)),
                Logger.red(item["displayName"]),
                Logger.cyan(item["bundleIdentifier"]),
                Logger.green(vsa_path),
            )
        )
        print("{}".format(Logger.blue(item["bundlePath"][8:])))
        print("{}".format(Logger.blue(data_path[8:])))
        print("{}\n".format(Logger.blue(item["executablePath"][8:])))
    session.detach()


if __name__ == "__main__":
    listApplicationDir("")
    # list_runing_process()
