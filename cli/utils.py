# /cli/utils.py
import typer
from pathlib import Path
from typing import List
from settings import config, t # 从 settings.py 导入全局配置 config 和翻译函数 t

def ensure_projects_dir():
    """确保项目目录存在，如果不存在则创建它。"""
    try:
        # config['settings']['projects_directory_full_path'] 在 settings.py 中已确保为字符串
        projects_full_path = Path(config['settings']['projects_directory_full_path'])
        if not projects_full_path.exists():
            projects_full_path.mkdir(parents=True, exist_ok=True)
            typer.echo(t('cli.TXT_PROJECT_DIR_CREATED', projects_dir=str(projects_full_path)))
    except KeyError:
        # 如果 settings.py 中 config 初始化失败，可能不存在这个键
        typer.secho("错误：配置中未找到 'projects_directory_full_path'。无法确保项目目录。", fg=typer.colors.RED, err=True)
    except Exception as e:
        # 其他创建目录时可能发生的错误
        projects_dir_str = config.get('settings', {}).get('projects_directory_full_path', '未知目录')
        typer.secho(f"错误：创建项目目录 {projects_dir_str} 失败: {e}", fg=typer.colors.RED, err=True)


def list_existing_projects_paths() -> List[Path]:
    """列出所有已存在项目的路径对象列表。"""
    ensure_projects_dir() # 首先确保项目根目录存在
    try:
        projects_full_path = Path(config['settings']['projects_directory_full_path'])
        if projects_full_path.exists() and projects_full_path.is_dir():
            # 返回目录中所有子目录的Path对象列表，并排序
            return sorted([d for d in projects_full_path.iterdir() if d.is_dir()])
    except KeyError:
        typer.secho("错误：配置中未找到 'projects_directory_full_path'。无法列出项目。", fg=typer.colors.RED, err=True)
    except Exception as e:
        projects_dir_str = config.get('settings', {}).get('projects_directory_full_path', '未知目录')
        typer.secho(f"错误：列出项目 {projects_dir_str} 中的项目失败: {e}", fg=typer.colors.RED, err=True)
    return [] # 出错或没有项目时返回空列表