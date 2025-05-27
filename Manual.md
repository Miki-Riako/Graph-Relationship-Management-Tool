# Graph Relationship Management Tool - CLI Manual

[![en](https://img.shields.io/badge/lang-en-blue.svg)](Manual.md) [![zh-cn](https://img.shields.io/badge/lang-zh--cn-red.svg)](Manual_CN.md) <!-- Assuming Manual_CN.md -->

**🚧 CURRENT STATUS: Early Development - Simple Demo 🚧**

This manual describes the command-line interface (CLI) for the Graph Relationship Management Tool. Please note that the tool is in its early development stages. The CLI is functional for basic operations but will be significantly enhanced in the future.

## 🌟 Overview

This tool provides a command-line interface to define, process, and visualize generic graph-based relationships. You can use it to model various systems, from personal knowledge maps to project dependencies.

The main executable script is `main.py`.

## 📁 Core Commands

Each graph is managed as a separate "project" within a dedicated directory (default: `projects/`).

### `python main.py new <project_name>`

Creates a new graph project. A directory named `<project_name>` will be created, containing a sample `graph.yaml` file to get you started.

*   **Usage:** `python main.py new <project_name>`
*   **Example:** `python main.py new MySystemMap`

### `python main.py list`

Lists all existing projects in your projects directory.

*   **Usage:** `python main.py list`

### `python main.py open <project_name> [OPTIONS]`

Processes an existing project's `graph.yaml` file. This command typically:
1.  Builds the graph from the YAML data.
2.  Prints basic graph statistics (node/edge count, etc.).
3.  Generates an interactive `skill_tree.html` file in the project's directory.
4.  Exports the graph to `skill_tree.gexf`.
5.  Starts a local HTTP server to serve the `skill_tree.html` and prints the URL.
6.  Enters a simple terminal query mode for exploring direct connections.

*   **Usage:** `python main.py open <project_name> [OPTIONS]`
*   **Options:**
    *   `--skip-vis`: Skip HTML generation and server start.
    *   `--skip-analyze`: Skip printing graph analysis.
    *   `--skip-export-gexf`: Skip GEXF export.
    *   `--skip-query`: Skip terminal query mode.
    *   `--serve-only`: Only start the HTTP server for an existing HTML file; does not reprocess the graph.
*   **Example:** `python main.py open MySystemMap`

### `python main.py shell`

Enters an interactive shell mode (`skilltree>`) where you can run `new`, `list`, `open`, and `help` commands without prefixing `python main.py`.

*   **Usage:** `python main.py shell`
*   **Inside shell:** `open MySystemMap`, `exit`

## 📝 Data File Format: `graph.yaml`

Graph data for each project is defined in a `graph.yaml` file within its directory (e.g., `projects/MySystemMap/graph.yaml`).

*   **Structure:**
    ```yaml
    nodes:  # List of node objects
      - id: NodeID1            # Required: Unique string identifier
        label: Display Label 1   # Optional: Text for display (defaults to id)
        # ... any other custom attributes (key-value pairs) ...
        # Example: type: "Person", status: "Active", color: "blue"

      - id: NodeID2
        label: Another Node
        # ...

    edges:  # List of edge objects
      - source: NodeID1      # Required: 'id' of the source node
        target: NodeID2      # Required: 'id' of the target node
        # ... any other custom attributes ...
        # Example: relationship: "CONNECTS_TO", weight: 5, directed: true
    ```
*   **Key Points:**
    *   Node `id`s must be unique.
    *   Edge `source` and `target` must refer to existing node `id`s.
    *   Use underscores in `id`s for simplicity; `label`s can have spaces.
    *   All attributes beyond the required ones are user-defined and will be part of the graph data.

## ⚙️ Configuration (`config.yaml`)

Global settings (default language, server port) are in `config.yaml` at the project root.

## 🌍 Language Support

CLI output supports English (`en`) and Simplified Chinese (`zh_cn`), set in `config.yaml`.

## 🛣️ Future Development

This tool is actively being developed. Key areas for future improvement include:

*   **More Sophisticated CLI:** Adding commands for granular graph editing (add/modify/delete nodes/edges), advanced querying, and more detailed analysis.
*   **Web-Based GUI:** The long-term vision includes a comprehensive web GUI for a more intuitive and visual graph management experience.
*   **Enhanced Visualizations:** More control over layout, styling, and interactivity.
*   **Data Management:** Support for larger datasets and potentially different storage backends.

Your feedback during this early stage is invaluable!
