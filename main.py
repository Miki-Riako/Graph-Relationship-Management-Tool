import os
import sys
from src.skill_tree_builder import SkillTreeProject

# --- Configuration ---
PROJECTS_DIR = 'projects'

def ensure_projects_dir():
    """确保 projects 目录存在。"""
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)
        print(f"已创建工程目录: '{PROJECTS_DIR}'")

def list_existing_projects():
    """列出所有已存在的工程名称。"""
    ensure_projects_dir()
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    return sorted(projects)

def display_main_menu():
    """显示主菜单并获取用户选择。"""
    print("\n--- Personal Skill Tree Builder ---")
    print("1. 创建新工程")
    print("2. 打开已有工程")
    print("3. 退出")
    choice = input("请选择操作 (1/2/3): ").strip()
    return choice

def create_new_project():
    """引导用户创建新工程。"""
    ensure_projects_dir()
    while True:
        project_name = input("请输入新工程名称 (例如: MyLearningJourney): ").strip()
        if not project_name:
            print("工程名称不能为空，请重新输入。")
            continue
        
        # 简单验证工程名称，避免路径问题
        if any(c in project_name for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            print("工程名称不能包含特殊字符 (如 / \\ : * ? \" < > |)，请重新输入。")
            continue
        
        project_path = os.path.join(PROJECTS_DIR, project_name)
        if os.path.exists(project_path):
            print(f"工程 '{project_name}' 已存在。请选择其他名称或打开已有工程。")
        else:
            try:
                os.makedirs(project_path)
                # 在新工程目录下创建空的 relations.txt 文件
                # 初始内容有助于用户理解如何填写
                with open(os.path.join(project_path, 'relations.txt'), 'w', encoding='utf-8') as f:
                    f.write("# 在此文件中定义您的知识关系，每行一条: Source_Concept -> Target_Concept\n")
                    f.write("# 示例:\n")
                    f.write("# Mathematics -> Calculus\n")
                    f.write("# CS -> Algorithms\n")
                    f.write("# Physics -> Mathematics\n")
                print(f"新工程 '{project_name}' 已创建在 '{project_path}'。")
                return project_path
            except Exception as e:
                print(f"创建工程时发生错误: {e}", file=sys.stderr)
                return None

def open_existing_project():
    """引导用户打开已有工程。"""
    projects = list_existing_projects()
    if not projects:
        print("目前没有可用的工程。请先创建一个新工程。")
        return None

    print("\n--- 可用的工程 ---")
    for i, project_name in enumerate(projects):
        print(f"{i+1}. {project_name}")
    
    while True:
        try:
            choice = input(f"请输入要打开的工程序号 (1-{len(projects)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                project_name = projects[idx]
                project_path = os.path.join(PROJECTS_DIR, project_name)
                print(f"正在打开工程 '{project_name}'...")
                return project_path
            else:
                print("无效的序号，请重新输入。")
        except ValueError:
            print("输入无效，请输入一个数字。")

def main():
    """主程序入口，处理用户交互和工程管理。"""
    ensure_projects_dir() # 确保 projects 目录在程序启动时就存在

    while True:
        choice = display_main_menu()
        current_project_path = None

        if choice == '1':
            current_project_path = create_new_project()
        elif choice == '2':
            current_project_path = open_existing_project()
        elif choice == '3':
            print("感谢使用，再见！")
            sys.exit(0)
        else:
            print("无效的选择，请重新输入 (1/2/3)。")
            continue # 返回主菜单重新选择

        if current_project_path:
            # 如果成功创建或打开了工程
            project_instance = SkillTreeProject(current_project_path)
            project_instance.run_workflow() # 运行该工程的完整工作流
            
            # 在一个工程处理完毕后，询问用户是否返回主菜单
            input("\n按回车键返回主菜单或 Ctrl+C 退出...")
            print("-" * 50)
            # 继续循环，返回主菜单
        else:
            # 如果创建或打开工程失败 (如工程名已存在或无可用工程)，则返回主菜单
            continue

if __name__ == "__main__":
    main()