# /cli/app.py
import typer
from settings import t # 从 settings.py 导入全局翻译函数 t

# 创建主要的 Typer 应用实例
# 这个实例将被 main.py 用来运行程序,
# 也会被 cli/commands.py 用来注册所有命令。
cli_app = typer.Typer(
    name="skilltree", # 可以给你的CLI应用起一个程序名，用于帮助信息
    help=t('cli.TXT_APP_TITLE'), # 应用的整体帮助信息
    pretty_exceptions_enable=False, # 开发时可以设为True，方便查看Typer格式化的异常
    # rich_markup_mode="markdown", # 如果你在帮助文本中使用Markdown，可以取消注释
    add_completion=False # 除非你特别配置了shell补全，否则可以先禁用
)

# 导入命令模块。这会执行 cli/commands.py 文件,
# 该文件中的 @cli_app.command() 装饰器会将命令注册到 cli_app 上。
# 必须在 cli_app 定义之后导入，以避免循环导入问题。
from . import commands