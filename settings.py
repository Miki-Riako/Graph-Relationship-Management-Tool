# /settings.py
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# --- 全局常量 ---
APP_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = APP_ROOT / 'config.yaml'
PROJECTS_DIR_NAME = 'projects'  # 如果配置中没有，则使用此默认值
LANG_DIR = APP_ROOT / 'lang'

# --- 全局变量 (稍后由函数填充) ---
config: Dict[str, Any] = {}
lang_strings: Dict[str, Any] = {}

def load_config_and_language():
    """加载配置和语言字符串到全局变量中。"""
    global config, lang_strings # 声明我们要修改模块级别的全局变量

    # 加载配置
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                # 确保加载的是字典，如果文件为空或格式错误，则 yaml.safe_load 可能返回 None
                config = loaded_config if isinstance(loaded_config, dict) else {}
        except yaml.YAMLError as e:
            print(f"错误：解析 config.yaml 失败: {e}。将使用空配置。", file=sys.stderr)
            config = {} # 出错时提供一个空的配置字典
        except IOError as e:
            print(f"错误：读取 config.yaml 失败: {e}。将使用空配置。", file=sys.stderr)
            config = {}
    else:
        print(f"提示：config.yaml 未找到。将在 {CONFIG_PATH} 创建默认配置。")
        config = {
            'settings': {
                'default_language': 'zh_cn', # 默认语言可以设为您常用的
                'projects_directory': PROJECTS_DIR_NAME,
                'auto_open_html': True,
                'web_server_port': 5000 # 假设未来可能用到
            }
        }
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, indent=2, default_flow_style=False, allow_unicode=True)
            print(f"默认配置已创建于 {CONFIG_PATH}")
        except IOError as e:
            print(f"错误：创建默认配置文件 {CONFIG_PATH} 失败: {e}", file=sys.stderr)

    # 确保 'settings' 键存在且其值为字典
    if 'settings' not in config or not isinstance(config.get('settings'), dict):
        config['settings'] = {} # 如果不存在或类型不符，则初始化为空字典

    # 确保 web_server_port 有一个默认值
    if 'web_server_port' not in config['settings']:
        config['settings']['web_server_port'] = 5000 # 默认端口

    # 设置 projects_directory_full_path
    # config['settings'].get() 提供了默认值，以防 'projects_directory' 未在 config.yaml 中定义
    projects_dir_relative = config['settings'].get('projects_directory', PROJECTS_DIR_NAME)
    # 将其转换为字符串路径，因为 SkillTreeProject 的 project_path 参数期望字符串
    config['settings']['projects_directory_full_path'] = str(APP_ROOT / projects_dir_relative)


    # 加载语言文件
    default_lang = config['settings'].get('default_language', 'zh_cn') # 从配置获取默认语言
    lang_file_path = LANG_DIR / f"{default_lang}.yaml"

    if lang_file_path.exists():
        try:
            with open(lang_file_path, 'r', encoding='utf-8') as f:
                loaded_lang = yaml.safe_load(f)
                lang_strings = loaded_lang if isinstance(loaded_lang, dict) else {}
        except yaml.YAMLError as e:
            print(f"错误：解析语言文件 {lang_file_path} 失败: {e}。本地化可能不完整。", file=sys.stderr)
            lang_strings = {}
        except IOError as e:
            print(f"错误：读取语言文件 {lang_file_path} 失败: {e}。本地化可能不完整。", file=sys.stderr)
            lang_strings = {}
    else:
        print(f"警告：语言文件 '{lang_file_path}' 未找到。将尝试回退到 'en' (英文)。", file=sys.stderr)
        en_file_path = LANG_DIR / "en.yaml"
        if en_file_path.exists():
            try:
                with open(en_file_path, 'r', encoding='utf-8') as f:
                    loaded_en_lang = yaml.safe_load(f)
                    lang_strings = loaded_en_lang if isinstance(loaded_en_lang, dict) else {}
                print("提示：已加载英文语言文件作为回退。")
            except Exception as e: # 捕获加载英文回退文件时可能发生的任何错误
                print(f"错误：加载英文回退语言文件 {en_file_path} 失败: {e}", file=sys.stderr)
                lang_strings = {} # 确保 lang_strings 是一个字典
        else:
            lang_strings = {} # 确保 lang_strings 是一个字典
            print(f"错误：默认的英文语言文件 '{en_file_path}' 也未找到。CLI 输出将显示键名而非翻译文本。", file=sys.stderr)

def get_t_function():
    """返回翻译函数 _t。"""
    # 此处的 lang_strings 引用的是本模块顶层定义的 lang_strings 变量
    def _t_internal(key: str, **kwargs: Any) -> str:
        path_parts = key.split('.')
        current_value: Any = lang_strings # 开始从完整的语言字典查找
        for part in path_parts:
            if not isinstance(current_value, dict) or part not in current_value:
                return f"MISSING_LANG_KEY:{key}" # 如果路径中断或键不存在
            current_value = current_value[part]

        if isinstance(current_value, str):
            try:
                # 使用 .format(**kwargs) 来替换占位符
                return current_value.format(**kwargs)
            except KeyError as e_format: # 如果 format 中的占位符在 kwargs 中找不到
                return f"LANG_FORMAT_ERROR:{key} (占位符错误: {e_format})"
            except Exception as e_general_format: # 其他可能的格式化错误
                 return f"LANG_FORMAT_UNEXPECTED_ERROR:{key} ({e_general_format})"
        # 如果语言文件中对应的值不是字符串 (例如，它是一个列表或另一个字典),
        # 则返回其字符串表示形式，避免程序崩溃。
        return str(current_value)
    return _t_internal

# --- 初始化操作 ---
# 当 settings.py 模块第一次被导入时，以下代码会自动执行：
load_config_and_language() # 加载配置和语言
t = get_t_function()       # 创建全局可用的翻译函数 t