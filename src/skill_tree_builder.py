import networkx as nx
from pyvis.network import Network
import os
import sys

class SkillTreeProject:
    """
    封装单个知识树工程的所有操作和数据。
    每个工程有自己的知识关系文件、HTML输出和GEXF输出。
    """
    def __init__(self, project_path):
        """
        初始化一个知识树工程实例。
        :param project_path: 该工程的根目录路径。
        """
        self.project_path = project_path
        self.relations_file = os.path.join(project_path, 'relations.txt')
        self.html_export_file = os.path.join(project_path, 'skill_tree.html')
        self.gexf_export_file = os.path.join(project_path, 'skill_tree.gexf')
        self.graph = None # 用于存储 networkx 图对象

    def load_relations(self):
        """
        从工程的知识关系文件中加载关系。
        """
        relations = []
        if not os.path.exists(self.relations_file):
            print(f"错误: 知识关系文件 '{self.relations_file}' 未找到。请确保文件存在并包含您的知识关系。", file=sys.stderr)
            return [] # 返回空列表而不是退出，允许程序继续运行但不处理关系

        try:
            with open(self.relations_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split('->')
                    if len(parts) == 2:
                        source = parts[0].strip().replace(' ', '_')
                        target = parts[1].strip().replace(' ', '_')
                        if source and target:
                            relations.append((source, target))
                    else:
                        print(f"警告: 文件 '{self.relations_file}' 第 {line_num} 行格式不正确，已跳过: '{line}'", file=sys.stderr)
        except Exception as e:
            print(f"读取文件 '{self.relations_file}' 时发生错误: {e}", file=sys.stderr)
            return []
            
        if not relations:
            print(f"警告: 文件 '{self.relations_file}' 中没有找到有效的知识关系。请检查文件内容。", file=sys.stderr)
        
        return relations

    def build_graph(self, relations):
        """
        使用 networkx 库构建有向知识图谱并存储到实例中。
        """
        G = nx.DiGraph()
        G.add_edges_from(relations)
        self.graph = G # 存储图对象
        return G

    def visualize_interactive(self):
        """
        使用 pyvis 库创建交互式知识图谱，并保存为HTML文件。
        """
        if not self.graph or not self.graph.nodes():
            print("图谱中没有节点，无法进行交互式可视化。")
            return

        net = Network(notebook=False, directed=True, height="750px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote')
        net.toggle_physics(True)

        for node, attrs in self.graph.nodes(data=True):
            node_size = 10 + self.graph.in_degree(node) * 5
            if node_size > 50: node_size = 50

            color = 'skyblue'
            if node in ['Mathematics', 'CS', 'Physics', 'EE']:
                color = '#FF5733'
                node_size = 40
            elif node in ['Calculus', 'Linear_Algebra', 'Algorithms', 'Operating_Systems', 'Electromagnetism', 'Circuits']:
                color = '#33FF57'
                node_size = 30
            
            net.add_node(node, label=node.replace('_', ' '), title=f"Concept: {node.replace('_', ' ')}", color=color, size=node_size)

        for source, target, attrs in self.graph.edges(data=True):
            net.add_edge(source, target, width=1.5, color='gray')

        net.set_options("""
        var options = {
          "nodes": {
            "borderWidth": 1,
            "borderWidthSelected": 2,
            "shadow": {
              "enabled": true
            }
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.8
              }
            },
            "font": {
              "size": 10
            },
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            }
          },
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.005,
              "springLength": 100,
              "springConstant": 0.18
            },
            "maxVelocity": 146,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
              "enabled": true,
              "iterations": 2000,
              "updateInterval": 25
            }
          },
          "interaction": {
            "navigationButtons": true,
            "zoomView": true
          }
        }
        """)

        net.write_html(self.html_export_file, notebook=False) # 关键修改：直接调用 write_html
        print(f"\n交互式图谱已保存为 '{self.html_export_file}'。请在浏览器中打开此文件。")

    def analyze_graph(self):
        """
        打印图谱的基本统计信息，包括节点、边数量，以及高入度和出度节点。
        """
        if not self.graph:
            print("图谱尚未构建，无法进行分析。")
            return

        print("\n--- Graph Overview ---")
        print(f"Total Nodes: {self.graph.number_of_nodes()}")
        print(f"Total Edges: {self.graph.number_of_edges()}")

        if not self.graph.nodes():
            return

        sorted_in_degree_items = sorted(self.graph.in_degree(), key=lambda item: item[1], reverse=True)
        print("\n--- Core Knowledge Points (High In-Degree Nodes) ---")
        for node, degree in sorted_in_degree_items[:min(5, len(sorted_in_degree_items))]:
            print(f"- {node}: In-Degree {degree}")

        sorted_out_degree_items = sorted(self.graph.out_degree(), key=lambda item: item[1], reverse=True)
        print("\n--- Major Branch Start Points (High Out-Degree Nodes) ---")
        for node, degree in sorted_out_degree_items[:min(5, len(sorted_out_degree_items))]:
            print(f"- {node}: Out-Degree {degree}")

    def interactive_lookup(self):
        """
        允许用户在终端输入概念名称，查询其前置和后续概念。
        """
        if not self.graph:
            print("图谱尚未构建，无法进行交互式查询。")
            return

        print("\n--- Lookup Specific Concept ---")
        print("输入 'exit' 退出查询模式。")
        while True:
            concept_name = input("请输入您想查询的概念 (例如: CS, Spinlock): ").strip().replace(' ', '_')
            if concept_name.lower() == 'exit':
                break

            if concept_name not in self.graph:
                print(f"'{concept_name}' 未在图谱中找到。请检查概念名称是否正确（区分大小写或下划线）。")
                continue

            successors = list(self.graph.successors(concept_name))
            print(f"\n'{concept_name}' 的直接后续概念 (它包含或指向的):")
            if successors:
                for s in successors:
                    print(f"- {s}")
            else:
                print("  无")

            predecessors = list(self.graph.predecessors(concept_name))
            print(f"\n'{concept_name}' 的直接前置概念 (依赖或包含它的):")
            if predecessors:
                for p in predecessors:
                    print(f"- {p}")
            else:
                print("  无")
            print("-" * 30)

    def export_gexf(self):
        """
        将图谱数据导出为 GEXF 格式。
        """
        if not self.graph or not self.graph.nodes():
            print("图谱中没有节点，无法导出为GEXF。")
            return
        try:
            nx.write_gexf(self.graph, self.gexf_export_file)
            print(f"图谱数据已导出为 '{self.gexf_export_file}'，可在 Gephi 等工具中打开进行高级分析和可视化。")
        except Exception as e:
            print(f"导出GEXF文件时发生错误: {e}", file=sys.stderr)

    def run_workflow(self):
        """
        为当前工程运行完整的知识图谱构建和分析流程。
        """
        print(f"正在处理工程 '{os.path.basename(self.project_path)}'...")
        print(f"正在加载知识关系文件: {self.relations_file}...")
        relations = self.load_relations()
        
        if not relations:
            print("没有加载到有效的知识关系，将跳过图谱构建和可视化步骤。")
            return # 不再强制退出，允许空项目存在

        print("正在构建知识图谱...")
        self.build_graph(relations)

        self.analyze_graph()
        self.export_gexf()

        print("正在生成交互式可视化图谱...")
        self.visualize_interactive()
        
        self.interactive_lookup()
        print(f"工程 '{os.path.basename(self.project_path)}' 处理完毕。")