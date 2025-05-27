# Personal Skill Tree Builder🌳
A Python-based tool to visually map and navigate your comprehensive knowledge landscape. This project helps combat knowledge dispersion by creating a macro-level "skill tree" or "knowledge graph," allowing you to see the relationships between broad domains and key concepts at a glance.

<!-- ![Skill Tree Concept Diagram](https://via.placeholder.com/800x450?text=Your+Skill+Tree+Visualization+Here) -->

## 💡 Why This Tool?

As polymaths and lifelong learners, we may accumulate vast amounts of knowledge across diverse fields like Mathematics, Computer Science, Electrical Engineering, and Languages. A common challenge is that this knowledge can become "discrete" – we know we've learned something but struggle to recall details or their connections to other concepts, especially if rarely used.

This tool addresses that by:

*   **Providing a Macro View:** Instead of atomized notes (which are still valuable for depth), it focuses on the high-level relationships between broad topics and major concepts.
*   **Enhancing Recall & Navigation:** By visualizing how concepts connect, you can quickly locate where a specific piece of knowledge fits into your overall understanding and how it relates to other fields.
*   **Identifying Gaps & Strengths:** See which areas are densely connected (your strengths) and which are isolated (potential areas for deeper integration or review).
*   **Facilitating Cross-Domain Thinking:** Encourage discovering analogies and foundational principles that span multiple disciplines.

## ✨ Features

*   **Simple Data Input:** Define your knowledge concepts and their relationships using an intuitive `source -> target` text file format.
*   **Graph Construction:** Utilizes the `networkx` library to build a directed graph representing your knowledge connections.
*   **Interactive Visual Representation:** Generates a clear, customizable, and **interactive** HTML visualization of your skill tree using `pyvis` (built on `vis.js`), allowing you to zoom, pan, and drag nodes.
*   **Basic Graph Analysis:** Provides insights into your knowledge structure, such as total nodes/edges, highly connected concepts (high in-degree), and major branch points (high out-degree).
*   **Terminal Exploration:** Allows you to query the graph from the terminal to see direct predecessors and successors of any concept.
*   **GEXF Export:** Capability to export the graph data in GEXF format, allowing for advanced analysis and more sophisticated static visualizations in tools like [Gephi](https://gephi.org/).

## 🚀 Getting Started
### Prerequisites

*   Python 3.x

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Miki-Riako/Personal-Skill-Tree-Builder.git
    cd Personal-Skill-Tree-Builder
    ```

2.  **Install required Python libraries:**
    It's highly recommended to use a virtual environment.

    ```bash
    # Create a virtual environment (optional but recommended)
    python -m venv venv
    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file as described below.)*

### Usage

1.  **Create `requirements.txt` (if not already present):**
    Before running `pip install -r requirements.txt`, ensure you have a `requirements.txt` file in the project root with the following content:

    ```txt
    networkx
    matplotlib # Optional, if you decide to use it for other static plots
    pyvis
    ```

2.  **Define Your Knowledge Relations:**
    Create a file named `relations.txt` in the root directory of the project. In this file, list your knowledge concepts and their relationships. Each line should represent a single relationship in the format `Source_Concept -> Target_Concept`.

    **Example `relations.txt`:**

    ```txt
    # This is your knowledge relations definition file.
    # Use 'Source_Concept -> Target_Concept' format for each relationship.
    # Lines starting with '#' are comments and will be ignored.

    # Top-level Domains
    Mathematics -> Calculus
    Mathematics -> Linear_Algebra
    CS -> Algorithms
    CS -> Operating_Systems
    Physics -> Electromagnetism
    EE -> Circuits

    # Cross-domain Relationships (Macro Level)
    Physics -> Mathematics
    EE -> Physics
    CS -> Mathematics
    Machine_Learning -> Linear_Algebra # ML depends on Linear Algebra

    # In-domain Refinements (still macro/key concepts)
    Operating_Systems -> Concurrency
    Concurrency -> Spinlock # Spinlock is a concurrency mechanism
    Spinlock -> CAS # CAS is an atomic operation used in spinlocks
    Electromagnetism -> Maxwell_Equations # Maxwell's Equations are central to Electromagnetism
    Calculus -> Consistent_Continuity # Consistent Continuity is a concept in Calculus
    ```

    **Tip:** Start with broad domains and their high-level connections first. Gradually add more specific, but still important, concepts as you refine your map.

3.  **Run the Script:**

    Execute the main script from your terminal:

    ```bash
    python main.py
    ```

    This will:
    *   Load your `relations.txt` file.
    *   Print some basic graph statistics to the terminal.
    *   Generate an interactive HTML visualization of your knowledge graph (`skill_tree.html`) in the project root. Open this file in any web browser to explore your graph!
    *   Export the graph data to a GEXF file (`skill_tree.gexf`) for advanced analysis in tools like Gephi.
    *   Prompt you to enter a concept to explore its direct connections within the graph via the terminal.

<!-- **Interactive HTML Visualization (`skill_tree.html`):**

(Imagine a screenshot or GIF here of an interactive graph in a browser, where you can zoom, pan, and drag nodes. You'll generate this once the `pyvis` issue is resolved!)
You can see nodes representing concepts, and arrows showing relationships. Top-level domains (like CS, Mathematics) might be larger or differently colored, indicating their foundational nature. You can click on nodes to select them, and drag them around to explore connections. -->

## 🗺️ Future Enhancements

This project is a starting point and can be extended in many exciting ways:

*   **More Sophisticated Data Input:**
    *   Support for YAML or JSON files to allow richer node and edge attributes (e.g., `skill_level`, `last_reviewed_date`, `relationship_type` like `IS_A`, `DEPENDS_ON`, `APPLIES_TO`).
*   **Advanced Graph Analysis:**
    *   Implement algorithms for community detection (identifying clusters of related knowledge), shortest path finding between concepts, or centrality measures (identifying most influential concepts).
*   **Different Layout Algorithms:**
    *   Further explore and implement other `vis.js` or `Graphviz` layout options to find the most aesthetically pleasing and informative representation for complex graphs.
*   **Integration with PKM Tools:**
    *   Scripts to convert knowledge graph data to formats compatible with Obsidian MOCs (Maps of Content), or to generate Anki flashcards for concepts you want to actively recall.
*   **GUI or Web Interface:**
    *   Develop a simple graphical user interface or a lightweight web application for easier data input and graph viewing, beyond just the generated HTML.