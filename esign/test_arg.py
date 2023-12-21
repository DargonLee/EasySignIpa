import argparse

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='My Command Line Tool')

# 添加主命令参数
parser.add_argument('--main_argument', help='Main command argument')

# 创建子命令解析器
subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

# 添加子命令 'subcommand1'
subparser1 = subparsers.add_parser('subcommand1', help='Description for subcommand1')
subparser1.add_argument('sub_arg1', help='Argument for subcommand1')

# 添加子命令 'subcommand2'
subparser2 = subparsers.add_parser('subcommand2', help='Description for subcommand2')
subparser2.add_argument('sub_arg2', help='Argument for subcommand2')

# 解析命令行参数
args = parser.parse_args()

# 处理主命令参数
print(f'Main Argument: {args.main_argument}')

# 处理子命令
if args.subcommand == 'subcommand1':
    print(f'Subcommand1 Argument: {args.sub_arg1}')
elif args.subcommand == 'subcommand2':
    print(f'Subcommand2 Argument: {args.sub_arg2}')
