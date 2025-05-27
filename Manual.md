# Skill Tree Builder CLI Manual

This manual provides a concise guide to using the `Skill Tree Builder` command-line interface (CLI) to manage your knowledge graphs.

## 🌟 Overview

The `Skill Tree Builder` is a simple, command-line driven tool designed to help you organize, visualize, and analyze your personal knowledge. It allows you to map relationships between concepts and visualize them interactively.

The main executable command is `skilltree`.

**Global Options:**

*   `--version`: Show the application's version and exit.
*   `--help`, `-h`: Show help message for the current command or subcommand.

## 📁 Core Commands

These commands allow you to create, list, and interact with your knowledge graph projects. Each project is stored in its own folder under the `projects/` directory.

### `skilltree new <project_name>`

Creates a new knowledge graph project. A new directory will be created under `projects/` with the specified name. Inside, it will contain a default `graph.yaml` file, ready for you to define your knowledge concepts and their relationships.

*   **Usage:**
    ```bash
    skilltree new <project_name>
    ```
*   **Arguments:**
    *   `<project_name>` (Required): The unique name for your new project. This will also be the name of its directory.
*   **Example:**
    ```bash
    skilltree new MyLearningPath
    # Output: New project 'MyLearningPath' created at 'projects/MyLearningPath'.
    # A 'graph.yaml' file has been created inside.
    ```
    *After creating, you will need to edit `projects/MyLearningPath/graph.yaml` to define your graph.*

### `skilltree open <project_name>`

Opens an existing project, processes its `graph.yaml` file, and then:
1.  Builds the knowledge graph.
2.  Prints a summary of the graph (nodes, edges, important concepts).
3.  Generates an interactive HTML visualization (`skill_tree.html`) in the project directory.
4.  Exports the graph data to a GEXF file (`skill_tree.gexf`) for advanced analysis in tools like Gephi.
5.  Enters an interactive terminal query mode, allowing you to explore concept connections.

This is the primary command to interact with your knowledge graph.

*   **Usage:**
    ```bash
    skilltree open <project_name> [OPTIONS]
    ```
*   **Arguments:**
    *   `<project_name>` (Required): The name of the project to open and process.
*   **Options:**
    *   `--skip-vis`: Do not generate or open the interactive HTML visualization.
    *   `--skip-analyze`: Do not perform and print basic graph analysis.
    *   `--skip-export-gexf`: Do not export the graph data to GEXF format.
    *   `--skip-query`: Do not enter the interactive terminal query mode after processing.
*   **Example:**
    ```bash
    skilltree open MyLearningPath
    # This will load 'MyLearningPath/graph.yaml', build the graph,
    # print analysis, generate 'MyLearningPath/skill_tree.html', etc.

    skilltree open MyLearningPath --skip-vis --skip-query
    # This will process 'MyLearningPath' project, but only perform analysis and GEXF export,
    # without generating the HTML visualization or entering query mode.
    ```

### `skilltree list`

Lists all existing knowledge graph projects found in the `projects/` directory.

*   **Usage:**
    ```bash
    skilltree list
    ```
*   **Example:**
    ```bash
    skilltree list
    # Output:
    # Available Projects:
    # 1. MyLearningPath
    # 2. HistoryOfScience
    ```

## ⚙️ Configuration

The `Skill Tree Builder` uses a `config.yaml` file located in the root directory of the application to store global settings. This file is automatically created with default values if it doesn't exist.

*   **File Location:** `config.yaml` (in the root directory, alongside `main.py`)
*   **Example `config.yaml`:**

    ```yaml
    # config.yaml
    settings:
      default_language: en # Supported: en, zh_cn (more to come)
      auto_open_html: true # Set to false to prevent automatic opening of HTML in browser
    ```
*   **How to edit:** You can manually edit this file in a text editor to change settings like the default language or whether the generated HTML file opens automatically.
    *(For now, we will not implement `skilltree config set/get` commands to keep it simple, but we can add them later if needed.)*

## 🌍 Language Support

The CLI output supports multiple languages. You can change the language by editing the `default_language` setting in your `config.yaml` file.

*   **Supported Languages:**
    *   `en` (English - default)
    *   `zh_cn` (Simplified Chinese)
*   **Example:** To set the language to Simplified Chinese, open `config.yaml` and change `default_language` to `zh_cn`.

## 📝 Data File Format: `graph.yaml`

Each project's knowledge graph data is defined in a `graph.yaml` file within its project directory (e.g., `projects/MyProject/graph.yaml`). This YAML format allows for flexible and rich definition of nodes (concepts) and edges (relationships) with custom attributes.

*   **Structure:**

    ```yaml
    # projects/<project_name>/graph.yaml

    # Nodes section: Define individual concepts/skills and their attributes
    # The 'id' is a unique identifier, 'label' is what's displayed.
    nodes:
      - id: Mathematics         # Required: Unique identifier
        label: Mathematics      # Optional: Text displayed on the node (defaults to id if not provided)
        level: foundational     # Custom attribute: Example - 'foundational', 'intermediate', 'advanced'
        description: "The formal science of number, quantity, and space." # Custom attribute
        tags: [core, STEM]      # Custom attribute: Example - list of tags

      - id: Calculus
        label: Calculus
        level: intermediate
        last_reviewed: "2023-11-01"
        tags: [math, analysis]

      - id: Machine_Learning
        label: Machine Learning
        level: advanced
        tags: [AI, CS, statistics]

    # Edges section: Define relationships between nodes and their attributes
    # Uses 'source' and 'target' IDs defined in the 'nodes' section.
    edges:
      - source: Mathematics
        target: Calculus
        type: HAS_SUBFIELD     # Custom attribute: Example - DEPENDS_ON, IS_A, HAS_SUBFIELD, APPLIES_TO
        strength: 0.9          # Custom attribute: Example - relationship strength (0.0 to 1.0)
        notes: "Calculus is a major branch of mathematics."

      - source: Machine_Learning
        target: Linear_Algebra
        type: DEPENDS_ON
        notes: "Linear Algebra provides fundamental tools for ML algorithms."

      - source: Operating_Systems
        target: Concurrency
        type: HAS_TOPIC # OS contains concurrency concepts
    ```

## 🗺️ Future Enhancements

This manual outlines the tool's current capabilities and immediate next steps. The `Skill Tree Builder` is designed to be extensible, with potential future enhancements including:

*   **Interactive Graph Editing (CLI based):** Commands to add/remove nodes and edges directly via CLI (e.g., `skilltree add-node <project> <id>`).
*   **Advanced Graph Analysis Commands:** Specific commands for `community-detection`, `shortest-path`, `centrality` measures.
*   **More Visualization Customization:** Deeper control over colors, node shapes, edge styles directly from `config.yaml` or command-line options.
*   **PKM Tool Integration:** Exporting to Obsidian MOCs or Anki flashcards.
