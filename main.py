# /main.py

# 1. 尽早导入 settings 模块。
#    这会执行 settings.py 中的代码，从而加载配置和语言文件。
#    settings.py 中定义的全局变量 `config`, `lang_strings`, 和翻译函数 `t`
#    将可以通过 `settings.config`, `settings.lang_strings`, `settings.t` 来访问。
import settings

# 2. 从 cli.app 模块导入 Typer 应用实例 `cli_app`。
#    导入 cli.app 会间接导入 cli.commands，从而完成所有命令的注册。
from cli.app import cli_app

# 关于翻译函数 `t` 的说明:
# - `src.core.SkillTreeProject` 类有自己的 `_t` 方法，它使用实例化时传入的 `self.lang` (即 `settings.lang_strings`)。
# - CLI 部分 (例如 Typer 的 help 参数, `cli/commands.py` 中的 `typer.echo` 消息)
#   使用的是从 `settings.py` 导入的全局 `settings.t` 函数。

if __name__ == "__main__":
    # 运行 Typer 应用。
    # 所有的配置加载和命令注册已经在上面的导入过程中完成了。
    cli_app()