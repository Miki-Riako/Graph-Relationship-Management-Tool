# /cli/commands.py
import typer
import os
import sys
from pathlib import Path

# HTTP服务器相关的导入
import http.server
import socketserver
import threading
import time # time 仍然可能用于其他地方，或者将来用于更精细的控制
from functools import partial

# 从 .app 模块导入 cli_app 实例
from .app import cli_app
# 从顶层 settings 模块导入全局变量
from settings import config, lang_strings, t
# 从 src.core 导入核心业务逻辑类
from src.core import SkillTreeProject
# 从 .utils 模块导入CLI辅助函数
from .utils import ensure_projects_dir, list_existing_projects_paths

# 全局变量，用于跟踪HTTP服务器线程和状态
_http_server_thread = None
_http_server_instance = None

# 为新项目提供的默认 graph.yaml 内容
DEFAULT_GRAPH_YAML = """
nodes:
  - id: Mathematics
    label: 数学
    level: foundational
    description: "关于数、量、形、空间的结构、次序与关系等的科学。"
    tags: [核心, STEM]
  - id: CS
    label: 计算机科学
    level: foundational
    tags: [核心, STEM]
  - id: Calculus
    label: 微积分
    level: intermediate
    last_reviewed: "2023-11-01"
    tags: [数学, 分析]
  - id: Linear_Algebra
    label: 线性代数
    level: intermediate
    tags: [数学, 基础]
  - id: Algorithms
    label: 算法
    tags: [计算机科学, 核心]
  - id: Machine_Learning
    label: 机器学习
    tags: [计算机科学, 人工智能]
  - id: Operating_Systems
    label: 操作系统
    tags: [计算机科学, 系统]
  - id: Concurrency
    label: 并发编程
    tags: [计算机科学, 编程]

edges:
  - source: Mathematics
    target: Calculus
    type: HAS_SUBFIELD
    strength: 0.9
  - source: Mathematics
    target: Linear_Algebra
    type: HAS_SUBFIELD
  - source: CS
    target: Algorithms
    type: HAS_SUBFIELD
  - source: CS
    target: Mathematics
    type: DEPENDS_ON
  - id: ml_depends_la
    source: Machine_Learning
    target: Linear_Algebra
    type: DEPENDS_ON
    notes: "理解底层模型的关键。"
  - source: Operating_Systems
    target: Concurrency
    type: HAS_TOPIC
"""

@cli_app.command(name="new", help=t('cli.TXT_NEW_COMMAND_HELP'))
def new_project_cmd(
    project_name: str = typer.Argument(..., help=t('cli.TXT_PROJECT_NAME_PROMPT_SHORT'))
):
    """创建一个新的技能树工程。"""
    ensure_projects_dir()
    projects_full_path = Path(config['settings']['projects_directory_full_path'])

    if not project_name or any(c in project_name for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']):
        typer.secho(t('cli.TXT_PROJECT_NAME_INVALID_CHARS') + " (且不允许包含空格)", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    project_path = projects_full_path / project_name
    if project_path.exists():
        typer.secho(t('cli.TXT_PROJECT_EXISTS', project_name=project_name), fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)
    else:
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            with open(project_path / 'graph.yaml', 'w', encoding='utf-8') as f:
                f.write(DEFAULT_GRAPH_YAML)
            typer.echo(t('cli.TXT_PROJECT_CREATED', project_name=project_name, project_path=str(project_path)))
            typer.echo(t('cli.TXT_NEW_PROJECT_HINT', project_name=project_name))
        except Exception as e:
            typer.secho(f"{t('cli.TXT_ERROR_CREATING_PROJECT')}: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

@cli_app.command(name="list", help=t('cli.TXT_LIST_COMMAND_HELP'))
def list_projects_cmd():
    """列出所有可用的技能树工程。"""
    projects = list_existing_projects_paths()
    if not projects:
        typer.echo(t('cli.TXT_NO_AVAILABLE_PROJECTS'))
        return

    typer.echo(t('cli.TXT_AVAILABLE_PROJECTS'))
    for i, project_path_obj in enumerate(projects):
        typer.echo(f"{i + 1}. {project_path_obj.name}")


def start_local_server(project_name_for_msg: str, project_path: Path, html_file_name: str, port: int):
    """
    在指定项目路径下，为特定的HTML文件启动一个本地HTTP服务器。
    """
    global _http_server_thread, _http_server_instance

    if _http_server_instance:
        typer.echo(t('cli.TXT_STOPPING_PREVIOUS_SERVER'))
        try:
            _http_server_instance.shutdown()
            _http_server_instance.server_close()
        except Exception as e_shutdown:
            typer.secho(f"关闭先前服务器时出错: {e_shutdown}", fg=typer.colors.YELLOW, err=True)

        if _http_server_thread and _http_server_thread.is_alive():
            _http_server_thread.join(timeout=2)
            if _http_server_thread.is_alive(): # 如果线程仍在运行
                 typer.secho(f"警告：先前的服务器线程未能完全停止。", fg=typer.colors.YELLOW, err=True)

    _http_server_instance = None
    _http_server_thread = None

    Handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(project_path))

    try:
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", port), Handler)
        _http_server_instance = httpd
    except OSError as e:
        if e.errno == 98: # Address already in use
            typer.secho(t('cli.TXT_PORT_IN_USE', port=port, error_message=str(e)), fg=typer.colors.RED, err=True)
            typer.echo(t('cli.TXT_PORT_IN_USE_HINT'))
            return None
        else:
            typer.secho(t('cli.TXT_SERVER_START_ERROR', error_message=str(e)), fg=typer.colors.RED, err=True)
            return None

    server_url = f"http://localhost:{port}/{html_file_name}"
    typer.echo("---")
    typer.echo(t('cli.TXT_SERVER_STARTED_AT_NO_CLIPBOARD', project_name=project_name_for_msg, html_file_name=html_file_name, url=server_url))
    # typer.echo(t('cli.TXT_SERVER_INFO_COPY_URL')) # 这句可以保留，或者合并到上面的消息中

    # 移除 pyperclip 相关逻辑
    # if os.name == 'nt' or 'WSL_DISTRO_NAME' in os.environ:
    #     try:
    #         import pyperclip
    #         pyperclip.copy(server_url)
    #         typer.echo(t('cli.TXT_URL_COPIED_TO_CLIPBOARD'))
    #     except (ImportError, pyperclip.PyperclipException): # type: ignore
    #         typer.echo(t('cli.TXT_PYPERCLIP_NOT_FOUND_HINT'))

    # 这个提示对于 shell 模式更有意义，表示服务器在后台运行
    typer.echo(t('cli.TXT_SERVER_RUNNING_IN_BACKGROUND_SHELL'))


    thread = threading.Thread(target=httpd.serve_forever, daemon=True) # daemon=True 很重要
    thread.start()
    _http_server_thread = thread
    return httpd


@cli_app.command(name="open", help=t('cli.TXT_OPEN_COMMAND_HELP'))
def open_project_cmd(
    project_name: str = typer.Argument(..., help=t('cli.TXT_PROJECT_NAME_TO_OPEN_PROMPT')),
    skip_vis: bool = typer.Option(False, "--skip-vis", help=t('cli.TXT_SKIP_VIS_HELP')),
    skip_analyze: bool = typer.Option(False, "--skip-analyze", help=t('cli.TXT_SKIP_ANALYZE_HELP')),
    skip_export_gexf: bool = typer.Option(False, "--skip-export-gexf", help=t('cli.TXT_SKIP_EXPORT_GEXF_HELP')),
    skip_query: bool = typer.Option(False, "--skip-query", help=t('cli.TXT_SKIP_QUERY_HELP')),
    serve_only: bool = typer.Option(False, "--serve-only", help=t('cli.TXT_SERVE_ONLY_HELP'))
):
    """打开并处理一个已存在的技能树工程，并可选地启动本地HTTP服务器提供可视化结果。"""
    projects_full_path = Path(config['settings']['projects_directory_full_path'])
    project_path = projects_full_path / project_name

    if not project_path.exists() or not project_path.is_dir():
        typer.secho(t('cli.TXT_PROJECT_NOT_FOUND', project_name=project_name), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    project_instance = SkillTreeProject(
        project_path=str(project_path),
        config=config.get('settings', {}),
        lang_strings=lang_strings
    )

    if not serve_only:
        project_instance.run_workflow(
            skip_vis=skip_vis,
            skip_analyze=skip_analyze,
            skip_export_gexf=skip_export_gexf,
            skip_query=skip_query
        )
    else:
        if not Path(project_instance.html_export_file).exists():
            typer.secho(t('cli.TXT_HTML_NOT_FOUND_FOR_SERVE_ONLY', file_path=project_instance.html_export_file), fg=typer.colors.RED, err=True)
            typer.echo(t('cli.TXT_HTML_NOT_FOUND_FOR_SERVE_ONLY_HINT', project_name=project_name))
            raise typer.Exit(code=1)
        typer.echo(t('cli.TXT_SERVE_ONLY_MODE_STARTING', file_path=project_instance.html_export_file))

    should_start_server = (config.get('settings', {}).get('auto_open_html', True) and not skip_vis) or serve_only

    if should_start_server:
        html_file_abs_path = Path(project_instance.html_export_file)
        if html_file_abs_path.exists():
            server_port = int(config['settings'].get('web_server_port', 5000))
            server_instance = start_local_server(
                project_name,
                project_path,
                html_file_abs_path.name,
                server_port
            )

            # 移除之前复杂的阻塞逻辑。
            # 如果是直接调用 `python main.py open demo`，命令执行完主程序退出，daemon服务器线程也退出。
            # 如果是在 shell 中调用，shell 的主循环会保持，daemon 服务器线程在后台运行。
            # 这通常是期望的行为。如果直接调用时也希望服务器持续运行，
            # 则需要用户自己通过其他方式保持 Python 进程（例如，不在 daemon 模式下运行线程，
            # 并在脚本末尾添加 input() 等待用户操作）。
            # 但对于CLI工具，默认执行完退出是合理的。

            if not server_instance: # 如果服务器启动失败 (例如端口占用)
                 typer.secho(t('cli.TXT_SERVER_NOT_STARTED_NO_BLOCK'), fg=typer.colors.YELLOW, err=True)

        else:
            typer.secho(t('cli.TXT_HTML_FILE_NOT_FOUND_FOR_SERVER', file_path=str(html_file_abs_path)), fg=typer.colors.RED, err=True)


@cli_app.command(name="shell", help=t('cli.TXT_SHELL_COMMAND_HELP'))
def interactive_shell_cmd():
    """进入交互式命令行模式。"""
    global _http_server_instance, _http_server_thread # 声明我们需要修改全局变量

    typer.echo(t('cli.TXT_WELCOME_TO_SHELL'))
    try:
        while True:
            try:
                prompt_text = t('cli.TXT_SHELL_PROMPT')
                command_line = typer.prompt(
                    prompt_text,
                    default="",
                    show_default=False,
                    prompt_suffix=": " if not prompt_text.strip().endswith((">", ":")) else " "
                ).strip()

                if not command_line:
                    continue
                if command_line.lower() in ["exit", "quit", "退出"]:
                    typer.echo(t('cli.TXT_THANK_YOU_EXIT'))
                    break # 退出 shell 循环

                args = command_line.split()
                if not args:
                    continue
                
                if args[0] == ":" and len(args) > 1:
                    args = args[1:]
                elif args[0] == ":":
                    continue

                if args[0].lower() == "help":
                    if len(args) == 1:
                        effective_args = ["--help"]
                    else:
                        effective_args = [args[1]] + ["--help"] + args[2:]
                else:
                    effective_args = args

                try:
                    prog_name_for_shell_cmd = cli_app.info.name if cli_app.info and hasattr(cli_app.info, 'name') else ""
                    cli_app(args=effective_args, standalone_mode=False, prog_name=prog_name_for_shell_cmd)

                except SystemExit as e_sys:
                    if e_sys.code is not None and e_sys.code != 0:
                        typer.secho(f"子命令以退出码 {e_sys.code} 终止 (SystemExit)。", fg=typer.colors.RED, err=True)
                except Exception as e_cmd_execution:
                    typer.secho(f"命令执行期间发生错误: {e_cmd_execution}", fg=typer.colors.RED, err=True)

            except typer.exceptions.Abort: # Ctrl+D in prompt
                typer.echo("\n" + t('cli.TXT_THANK_YOU_EXIT'))
                break # 退出 shell 循环
            except KeyboardInterrupt: # Ctrl+C in prompt or between commands
                typer.echo("\n" + t('cli.TXT_INTERRUPT_SHELL_PROMPT_AGAIN')) # 提示用户可以再次尝试或退出
                continue # 返回到 prompt，而不是退出 shell
            except Exception as e_shell_loop_internal:
                typer.secho(f"Shell 内部循环发生严重错误: {e_shell_loop_internal}", fg=typer.colors.RED, err=True)
                # 通常这意味着shell本身可能不稳定，可以选择 break 退出
                # import traceback
                # traceback.print_exc()

    finally:
        # 当shell退出时（通过exit, quit, 或未捕获的Ctrl+D/Ctrl+C导致的循环终止）
        if _http_server_instance:
            typer.echo(t('cli.TXT_SHELL_EXITING_STOPPING_SERVER'))
            try:
                _http_server_instance.shutdown()
                _http_server_instance.server_close()
            except Exception as e_final_shutdown:
                 typer.secho(f"Shell退出时关闭服务器出错: {e_final_shutdown}", fg=typer.colors.YELLOW, err=True)
            if _http_server_thread and _http_server_thread.is_alive():
                _http_server_thread.join(timeout=1)
            _http_server_instance = None
            _http_server_thread = None
        typer.echo(t('cli.TXT_SHELL_GOODBYE'))