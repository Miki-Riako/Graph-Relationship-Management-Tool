import os
import sys
import typer
import yaml
import webbrowser
from pathlib import Path
from dotenv import load_dotenv 
from typing import Optional, List
import io 

# --- Global Configuration and Language Loading ---
APP_ROOT = Path(__file__).parent
CONFIG_PATH = APP_ROOT / 'config.yaml'
PROJECTS_DIR_NAME = 'projects' 
LANG_DIR = APP_ROOT / 'lang'

config = {}
lang_strings = {}

# 在 Typer app 实例化之前加载配置和语言，确保_t函数可用
_load_config_and_language_early = True # 用于控制加载顺序

if _load_config_and_language_early:
    # 提前加载配置
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {
            'settings': {
                'default_language': 'en',
                'projects_directory': PROJECTS_DIR_NAME,
                'auto_open_html': True,
                'web_server_port': 5000
            }
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, indent=2, default_flow_style=False, allow_unicode=True)
        # 注意: 这里不能直接使用 typer.echo，因为typer可能还没完全初始化
        print(f"Default config created at {CONFIG_PATH}")
    
    projects_dir_relative = config.get('settings', {}).get('projects_directory', PROJECTS_DIR_NAME)
    config['settings']['projects_directory_full_path'] = APP_ROOT / projects_dir_relative

    # 提前加载语言
    default_lang = config.get('settings', {}).get('default_language', 'en')
    lang_file_path = LANG_DIR / f"{default_lang}.yaml"
    if lang_file_path.exists():
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            lang_strings = yaml.safe_load(f) or {}
    else:
        print(f"Warning: Language file '{lang_file_path}' not found. Falling back to default English.", file=sys.stderr)
        en_file_path = LANG_DIR / "en.yaml"
        if en_file_path.exists():
            with open(en_file_path, 'r', encoding='utf-8') as f:
                lang_strings = yaml.safe_load(f) or {}
        else:
            print(f"Error: Default English language file '{en_file_path}' not found. CLI output may be unlocalized.", file=sys.stderr)

# 现在_t函数和lang_strings应该是可用的
def _t(key, **kwargs):
    """翻译辅助函数"""
    path = key.split('.')
    value = lang_strings
    for p in path:
        if not isinstance(value, dict) or p not in value:
            return f"MISSING_LANG_KEY:{key}"
        value = value[p]

    if isinstance(value, str):
        return value.format(**kwargs)
    return value 

# 导入 SkillTreeProject 类 (放在_t函数定义之后，因为SkillTreeProject也可能使用_t)
from src.core import SkillTreeProject

# Typer app 实例现在可以在语言加载后安全地创建
app = typer.Typer(
    pretty_exceptions_enable=False, 
    help=_t('cli.TXT_APP_TITLE') # 使用翻译后的应用标题
    # rich_markup_enable=True 
)

# --- Helper Functions (CLI specific) ---

def _ensure_projects_dir():
    """确保 projects 目录存在。"""
    projects_full_path = config['settings']['projects_directory_full_path']
    if not projects_full_path.exists():
        projects_full_path.mkdir(parents=True, exist_ok=True)
        typer.echo(_t('cli.TXT_PROJECT_DIR_CREATED', projects_dir=projects_full_path))
        
def _list_existing_projects_paths() -> List[Path]:
    """列出所有已存在的工程的完整路径。"""
    _ensure_projects_dir()
    projects_full_path = config['settings']['projects_directory_full_path']
    projects = [d for d in projects_full_path.iterdir() if d.is_dir()]
    return sorted(projects)

# --- CLI Commands ---

@app.command(name="new", help=_t('cli.TXT_NEW_COMMAND_HELP'))
def new_project(
    project_name: str = typer.Argument(..., help=_t('cli.TXT_PROJECT_NAME_PROMPT_SHORT'))
):
    """
    创建新工程。
    """
    _ensure_projects_dir()
    projects_full_path = config['settings']['projects_directory_full_path']
    
    if not project_name or any(c in project_name for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
        typer.echo(_t('cli.TXT_PROJECT_NAME_INVALID_CHARS'))
        raise typer.Exit(code=1)
    
    project_path = projects_full_path / project_name
    if project_path.exists():
        typer.echo(_t('cli.TXT_PROJECT_EXISTS', project_name=project_name))
        raise typer.Exit(code=1)
    else:
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            default_yaml_content = """
nodes:
  - id: Mathematics
    label: Mathematics
    level: foundational
    description: "The formal science of number, quantity, and space."
    tags: [core, STEM]
  - id: CS
    label: Computer Science
    level: foundational
    tags: [core, STEM]
  - id: Calculus
    label: Calculus
    level: intermediate
    last_reviewed: "2023-11-01"
    tags: [math, analysis]
  - id: Linear_Algebra
    label: Linear Algebra
    level: intermediate
    tags: [math, foundations]

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
  - source: Machine_Learning
    target: Linear_Algebra
    type: DEPENDS_ON
    notes: "Crucial for understanding underlying models."
  - source: Operating_Systems
    target: Concurrency
    type: HAS_TOPIC
"""
            with open(project_path / 'graph.yaml', 'w', encoding='utf-8') as f:
                f.write(default_yaml_content)
            typer.echo(_t('cli.TXT_PROJECT_CREATED', project_name=project_name, project_path=project_path))
            typer.echo(_t('cli.TXT_NEW_PROJECT_HINT', project_name=project_name))
        except Exception as e:
            typer.echo(f"{_t('cli.TXT_ERROR_CREATING_PROJECT')}: {e}", err=True)
            raise typer.Exit(code=1)

@app.command(name="list", help=_t('cli.TXT_LIST_COMMAND_HELP'))
def list_projects():
    """
    列出所有已存在的工程名称。
    """
    projects = _list_existing_projects_paths()
    if not projects:
        typer.echo(_t('cli.TXT_NO_AVAILABLE_PROJECTS'))
        return

    typer.echo(_t('cli.TXT_AVAILABLE_PROJECTS'))
    for i, project_path in enumerate(projects):
        typer.echo(f"{i+1}. {project_path.name}")

@app.command(name="open", help=_t('cli.TXT_OPEN_COMMAND_HELP'))
def open_project(
    project_name: str = typer.Argument(..., help=_t('cli.TXT_PROJECT_NAME_TO_OPEN_PROMPT')),
    skip_vis: bool = typer.Option(False, "--skip-vis", help=_t('cli.TXT_SKIP_VIS_HELP')),
    skip_analyze: bool = typer.Option(False, "--skip-analyze", help=_t('cli.TXT_SKIP_ANALYZE_HELP')),
    skip_export_gexf: bool = typer.Option(False, "--skip-export-gexf", help=_t('cli.TXT_SKIP_EXPORT_GEXF_HELP')),
    skip_query: bool = typer.Option(False, "--skip-query", help=_t('cli.TXT_SKIP_QUERY_HELP'))
):
    """
    打开并处理已有工程。
    """
    projects_full_path = config['settings']['projects_directory_full_path']
    project_path = projects_full_path / project_name

    if not project_path.exists() or not project_path.is_dir():
        typer.echo(_t('cli.TXT_PROJECT_NOT_FOUND', project_name=project_name), err=True)
        raise typer.Exit(code=1)

    project_instance = SkillTreeProject(
        project_path=project_path,
        config=config['settings'],
        lang_strings=lang_strings # 传入整个语言字典
    )
    
    project_instance.run_workflow(
        skip_vis=skip_vis,
        skip_analyze=skip_analyze,
        skip_export_gexf=skip_export_gexf,
        skip_query=skip_query
    )

    if config.get('settings', {}).get('auto_open_html', True) and not skip_vis:
        html_file = project_instance.html_export_file
        if os.path.exists(html_file):
            typer.echo(f"Opening {html_file} in browser...")
            webbrowser.open_new_tab(f"file:///{os.path.abspath(html_file)}")

@app.command(name="shell", help=_t('cli.TXT_SHELL_COMMAND_HELP'))
def interactive_shell():
    """
    进入交互式Shell模式。
    """
    typer.echo(_t('cli.TXT_WELCOME_TO_SHELL'))
    
    shell_app = app 

    while True:
        try:
            command_line = typer.prompt(_t('cli.TXT_SHELL_PROMPT'))
            command_line = command_line.strip()

            if not command_line:
                continue
            if command_line.lower() in ["exit", "quit"]:
                typer.echo(_t('cli.TXT_THANK_YOU_EXIT'))
                break

            args = command_line.split()
            if not args:
                continue

            # --- 关键修改：处理 'help' 命令和捕获输出 ---
            # 如果用户输入 'help' (不带 --)，就将其转换为 Typer 的全局 --help
            if args[0].lower() == "help":
                args = ["--help"] + args[1:] # 转换为 ["--help", "arg1", "arg2"]
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            redirected_stdout = io.StringIO()
            redirected_stderr = io.StringIO()
            sys.stdout = redirected_stdout
            sys.stderr = redirected_stderr

            try:
                # 捕获 Typer.Exit 是为了让 shell 循环继续
                # 捕获 SystemExit 是为了处理 sys.exit()
                shell_app(args=args, standalone_mode=False) # standalone_mode=False 是关键，阻止其直接调用 sys.exit()

            except typer.Exit as e:
                if e.code != 0: # 如果是非零退出码，表示命令执行失败
                    sys.stderr.write(f"Command execution failed with code {e.code}.\n")
            except SystemExit as e: # 捕获直接由 sys.exit() 引起的 SystemExit
                if e.code != 0:
                    sys.stderr.write(f"Command execution failed with code {e.code} (SystemExit).\n")
            except Exception as e:
                sys.stderr.write(f"An unexpected error occurred during command execution: {e}\n")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                output = redirected_stdout.getvalue()
                error_output = redirected_stderr.getvalue()
                if output:
                    typer.echo(output.strip())
                if error_output:
                    typer.echo(error_output.strip(), err=True)

        except KeyboardInterrupt:
            typer.echo("\n" + _t('cli.TXT_THANK_YOU_EXIT'))
            break
        except Exception as e:
            typer.echo(f"Critical error in shell loop: {e}", err=True)

# --- Main entry point ---
if __name__ == "__main__":
    # 在 Typer app() 运行之前，确保语言和配置都已加载
    # 这一部分现在由函数顶部的_load_config_and_language_early处理，更安全
    app() # 运行 Typer 应用程序