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

    @staticmethod
    def cyan(msg):
        return Logger.CYAN + msg + Logger.END

    @staticmethod
    def blue(msg):
        return Logger.BLUE + msg + Logger.END

    @staticmethod
    def white(msg):
        return Logger.WHITE + msg + Logger.END

    @staticmethod
    def red(msg):
        return Logger.RED + msg + Logger.END

    @staticmethod
    def green(msg):
        return Logger.GREEN + msg + Logger.END

    @staticmethod
    def yellow(msg):
        return Logger.YELLOW + msg + Logger.END

    @staticmethod
    def info(msg):
        print(Logger.WHITE + msg + Logger.END)

    @staticmethod
    def warning(msg):
        print(Logger.YELLOW + msg + Logger.END)

    @staticmethod
    def error(msg):
        print(Logger.RED + msg + Logger.END)


if __name__ == "__main__":
    print(Logger.red("I am red! {}".format(["Lee", "Lee1"])))
    print(Logger.green("I am green!"))
    print(Logger.yellow("I am yellow!"))
    print(Logger.blue("I am blue!"))
    print(Logger.cyan("I am cyan!"))
    print(Logger.white("I am white!"))
