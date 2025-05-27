import networkx as nx
from pyvis.network import Network
import os
import yaml # 导入 PyYAML 库

class SkillTreeProject:
    """
    封装单个知识树工程的所有操作和数据。
    每个工程有自己的知识关系文件、HTML输出和GEXF输出。
    """
    def __init__(self, project_path, config=None, lang_strings=None):
        """
        初始化一个知识树工程实例。
        :param project_path: 该工程的根目录路径。
        :param config: 全局配置字典。
        :param lang_strings: 语言字符串字典。
        """
        self.project_path = project_path
        self.relations_file = os.path.join(project_path, 'graph.yaml') # 改为 YAML 文件
        self.html_export_file = os.path.join(project_path, 'skill_tree.html') # 统一命名
        self.gexf_export_file = os.path.join(project_path, 'skill_tree.gexf') # 统一命名
        self.graph = None # 用于存储 networkx 图对象
        self.config = config if config is not None else {}
        self.lang = lang_strings if lang_strings is not None else {}

    def _t(self, key, **kwargs):
        """翻译辅助函数 (与 main.py 中的 _t 保持一致的健壮性)"""
        path = key.split('.')
        value = self.lang
        for p in path:
            if not isinstance(value, dict) or p not in value: # 检查当前值是否为字典且键是否存在
                return f"MISSING_LANG_KEY:{key}"
            value = value[p]

        if isinstance(value, str):
            return value.format(**kwargs)
        return value 

    def load_relations(self):
        """
        从工程的知识关系YAML文件中加载关系。
        预期YAML结构：
        nodes:
          - id: ConceptA
            label: Concept A
            # ... other node attributes
        edges:
          - source: ConceptA
            target: ConceptB
            type: DEPENDS_ON
            # ... other edge attributes
        """
        print(self._t('skill_tree_project.TXT_LOADING_RELATIONS_FILE', file_path=self.relations_file))

        if not os.path.exists(self.relations_file):
            print(self._t('skill_tree_project.TXT_ERROR_RELATIONS_FILE_NOT_FOUND', file_path=self.relations_file))
            return False # 返回 False 表示加载失败

        try:
            with open(self.relations_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None: 
                    print(self._t('skill_tree_project.TXT_WARNING_NO_VALID_RELATIONS', file_path=self.relations_file))
                    self.graph = nx.DiGraph() # 创建一个空图以防止后续操作报错
                    return False # 返回 False 表示无有效关系

                nodes_data = data.get('nodes', [])
                edges_data = data.get('edges', [])

                G = nx.DiGraph()

                for node_info in nodes_data:
                    node_id = node_info.get('id')
                    if not node_id: # 确保id存在
                        print(f"警告: 节点定义缺少 'id' 字段：{node_info}，已跳过此节点。")
                        continue
                        
                    node_label = node_info.get('label', node_id).replace('_', ' ')
                    
                    attrs_to_add = {k: v for k, v in node_info.items() if k not in ['id', 'label']}
                    
                    # --- GEXF 兼容性修复 (tags 列表转字符串) ---
                    if 'tags' in attrs_to_add and isinstance(attrs_to_add['tags'], list):
                        attrs_to_add['tags'] = ",".join(map(str, attrs_to_add['tags'])) # Convert list to comma-separated string
                    # ----------------------------------------
                    
                    G.add_node(node_id, label=node_label, **attrs_to_add)

                for edge_info in edges_data:
                    source_id = edge_info.get('source')
                    target_id = edge_info.get('target')
                    if not source_id or not target_id:
                        print(f"警告: 边定义格式不正确，缺少 'source' 或 'target' 字段：{edge_info}，已跳过此边。")
                        continue

                    # 确保源和目标节点存在，避免 Key Error
                    if source_id not in G:
                        print(f"警告: 边 '{source_id} -> {target_id}' 的源节点 '{source_id}' 未定义在 'nodes' 部分，已跳过此边。")
                        continue
                    if target_id not in G:
                        print(f"警告: 边 '{source_id} -> {target_id}' 的目标节点 '{target_id}' 未定义在 'nodes' 部分，已跳过此边。")
                        continue
                    
                    attrs_to_add_edge = {k: v for k, v in edge_info.items() if k not in ['source', 'target']}
                    
                    # --- GEXF 兼容性修复 (strength 强制转换为 float) ---
                    if 'strength' in attrs_to_add_edge:
                        try:
                            attrs_to_add_edge['strength'] = float(attrs_to_add_edge['strength'])
                        except (ValueError, TypeError):
                            print(f"警告: 边 '{source_id} -> {target_id}' 的 'strength' 属性值 '{attrs_to_add_edge['strength']}' 无法转换为数字，将跳过此属性。")
                            del attrs_to_add_edge['strength'] # Remove if conversion fails
                    # --------------------------------------------------

                    G.add_edge(source_id, target_id, **attrs_to_add_edge)

                self.graph = G 
                
                if not G.nodes():
                    print(self._t('skill_tree_project.TXT_WARNING_NO_VALID_RELATIONS', file_path=self.relations_file))
                    return False # 返回 False 表示无有效关系
                
                return True # 加载成功
        except yaml.YAMLError as e:
            print(self._t('skill_tree_project.TXT_ERROR_READING_FILE', file_path=self.relations_file, error_message=e))
            return False
        except Exception as e:
            print(self._t('skill_tree_project.TXT_ERROR_READING_FILE', file_path=self.relations_file, error_message=e))
            return False

    def build_graph(self, relations_data=None):
        """
        这个函数现在主要是为了兼容之前的调用，实际的图构建逻辑已集成到 load_relations 中。
        """
        # 如果 self.graph 已经在 load_relations 中构建，则直接返回
        if self.graph:
            return self.graph
        # 否则，如果提供了 relations_data 并且 self.graph 为空，则构建
        elif relations_data: # relations_data 应该是列表形式的 (source, target, attrs)
            G = nx.DiGraph()
            for s, t, data in relations_data:
                G.add_edge(s, t, **data)
            self.graph = G
            return self.graph
        return None # 无法构建图

    def visualize_interactive(self):
        """
        使用 pyvis 库创建交互式知识图谱，并保存为HTML文件。
        """
        if not self.graph or not self.graph.nodes():
            print(self._t('skill_tree_project.TXT_NO_NODES_FOR_VIZ'))
            return

        net = Network(notebook=False, directed=True, height="750px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote')
        net.toggle_physics(True)

        for node_id, attrs in self.graph.nodes(data=True):
            node_label = attrs.get('label', node_id).replace('_', ' ')

            node_size = 10 + self.graph.in_degree(node_id) * 5
            if node_size > 50: node_size = 50

            color = 'skyblue'
            if attrs.get('level') == 'foundational':
                color = '#FF5733'
                node_size = max(node_size, 40)
            elif attrs.get('level') == 'intermediate':
                color = '#33FF57'
            
            node_title = f"Concept: {node_label}"
            if 'description' in attrs:
                node_title += f"\nDescription: {attrs['description']}"
            if 'tags' in attrs:
                # pyvis 对字符串和列表通常都兼容，但如果 tags 已经被转为字符串，这里直接用
                if isinstance(attrs['tags'], list):
                    node_title += f"\nTags: {', '.join(map(str, attrs['tags']))}"
                else: # 已经是字符串或非列表类型
                    node_title += f"\nTags: {attrs['tags']}"
            
            net.add_node(node_id, label=node_label, title=node_title, color=color, size=node_size)

        for source, target, attrs in self.graph.edges(data=True):
            edge_color = 'gray'
            if attrs.get('type') == 'DEPENDS_ON':
                edge_color = 'orange'
            elif attrs.get('type') == 'HAS_SUBFIELD':
                edge_color = 'lightblue'

            edge_title = f"Relationship: {attrs.get('type', 'Generic')}"
            if 'notes' in attrs:
                edge_title += f"\nNotes: {attrs['notes']}"
            
            # GEXF 兼容性修复中 strength 已经转为 float，pyvis 接受 float
            net.add_edge(source, target, width=1.5, color=edge_color, title=edge_title)

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

        net.write_html(self.html_export_file, notebook=False)
        print(self._t('skill_tree_project.TXT_HTML_SAVED', file_path=self.html_export_file))

    def analyze_graph(self):
        """
        打印图谱的基本统计信息，包括节点、边数量，以及高入度和出度节点。
        """
        if not self.graph:
            print(self._t('skill_tree_project.TXT_GRAPH_NOT_BUILT_ANALYSIS'))
            return

        print(self._t('skill_tree_project.TXT_GRAPH_OVERVIEW'))
        print(self._t('skill_tree_project.TXT_TOTAL_NODES'), self.graph.number_of_nodes())
        print(self._t('skill_tree_project.TXT_TOTAL_EDGES'), self.graph.number_of_edges())

        if not self.graph.nodes():
            return

        sorted_in_degree_items = sorted(self.graph.in_degree(), key=lambda item: item[1], reverse=True)
        print(self._t('skill_tree_project.TXT_CORE_KNOWLEDGE_POINTS'))
        for node, degree in sorted_in_degree_items[:min(5, len(sorted_in_degree_items))]:
            print(f"- {node}: {self._t('skill_tree_project.TXT_IN_DEGREE')} {degree}")

        sorted_out_degree_items = sorted(self.graph.out_degree(), key=lambda item: item[1], reverse=True)
        print(self._t('skill_tree_project.TXT_MAJOR_BRANCH_START_POINTS'))
        for node, degree in sorted_out_degree_items[:min(5, len(sorted_out_degree_items))]:
            print(f"- {node}: {self._t('skill_tree_project.TXT_OUT_DEGREE')} {degree}")

    def interactive_lookup(self):
        """
        允许用户在终端输入概念名称，查询其前置和后续概念。
        """
        if not self.graph:
            print(self._t('skill_tree_project.TXT_GRAPH_NOT_BUILT_LOOKUP'))
            return

        print(self._t('skill_tree_project.TXT_LOOKUP_SPECIFIC_CONCEPT'))
        print(self._t('skill_tree_project.TXT_ENTER_EXIT_TO_QUIT'))
        while True:
            concept_name = input(self._t('skill_tree_project.TXT_CONCEPT_NAME_PROMPT')).strip().replace(' ', '_')
            if concept_name.lower() == 'exit':
                break

            if concept_name not in self.graph:
                print(self._t('skill_tree_project.TXT_CONCEPT_NOT_FOUND', concept_name=concept_name))
                continue

            successors = list(self.graph.successors(concept_name))
            print(self._t('skill_tree_project.TXT_SUCCESSORS', concept_name=concept_name))
            if successors:
                for s in successors:
                    print(f"- {s}")
            else:
                print(f"  {self._t('skill_tree_project.TXT_NONE')}")

            predecessors = list(self.graph.predecessors(concept_name))
            print(self._t('skill_tree_project.TXT_PREDECESSORS', concept_name=concept_name))
            if predecessors:
                for p in predecessors:
                    print(f"- {p}")
            else:
                print(f"  {self._t('skill_tree_project.TXT_NONE')}")
            print("-" * 30)

    def export_gexf(self):
        """
        将图谱数据导出为 GEXF 格式。
        """
        if not self.graph or not self.graph.nodes():
            print(self._t('skill_tree_project.TXT_NO_NODES_FOR_GEXF'))
            return
        try:
            nx.write_gexf(self.graph, self.gexf_export_file)
            print(self._t('skill_tree_project.TXT_GEXF_EXPORTED', file_path=self.gexf_export_file))
        except Exception as e:
            print(self._t('skill_tree_project.TXT_ERROR_EXPORTING_GEXF', error_message=e))

    def run_workflow(self, skip_vis=False, skip_analyze=False, skip_export_gexf=False, skip_query=False):
        """
        为当前工程运行完整的知识图谱构建和分析流程。
        :param skip_vis: 是否跳过可视化。
        :param skip_analyze: 是否跳过分析。
        :param skip_export_gexf: 是否跳过GEXF导出。
        :param skip_query: 是否跳过交互式查询。
        """
        print(self._t('cli.TXT_OPENING_PROJECT', project_name=os.path.basename(self.project_path)))
        
        # load_relations 现在直接构建图，并返回是否成功
        load_success = self.load_relations() 
        
        if not load_success or not self.graph or not self.graph.nodes():
            print(self._t('skill_tree_project.TXT_NO_RELATIONS_WORKFLOW_SKIPPED'))
            return

        print(self._t('skill_tree_project.TXT_BUILDING_GRAPH')) # 此时图已构建，此行仅作提示

        if not skip_analyze:
            self.analyze_graph()
        if not skip_export_gexf:
            self.export_gexf()

        if not skip_vis:
            # 这里的打印现在是完整的本地化字符串，不需要split
            print(self._t('skill_tree_project.TXT_HTML_SAVED', file_path=self.html_export_file)) 
            self.visualize_interactive()
        
        if not skip_query:
            self.interactive_lookup()
        
        print(self._t('cli.TXT_PROJECT_PROCESSED', project_name=os.path.basename(self.project_path)))