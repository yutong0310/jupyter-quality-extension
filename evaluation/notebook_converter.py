import os
import nbformat
from nbconvert import PythonExporter
from IPython.display import display, HTML

def convert_notebooks_in_dir(root_dir):
    """
    Converts all .ipynb notebooks under a directory (recursively) into .py Python files.

    This function modifies the folder in-place by generating .py files next to each .ipynb file. 
    These .py files will then be automatically picked up by the existing scanning logic in `evaluate_metrics()`.

    Args:
        root_dir (str): Path to the directory to recursively scan.
    """
    if os.path.isfile(root_dir) and root_dir.endswith(".ipynb"):
        # Single file case
        _convert_notebook_file(root_dir)
    elif os.path.isdir(root_dir):
        # Directory case
        for dirpath, _, filenames in os.walk(root_dir):
            # Skip .ipynb_checkpoints directories
            if ".ipynb_checkpoints" in dirpath:
                continue

            for file in filenames:
                if file.endswith(".ipynb") and not file.startswith("."):
                    notebook_path = os.path.join(dirpath, file)
                    _convert_notebook_file(notebook_path)
    else:
        print(f"[WARNING] Path not found or not valid: {root_dir}")

def _convert_notebook_file(notebook_path):
    """Helper to convert a single .ipynb notebook to a .py file"""
    py_path = os.path.splitext(notebook_path)[0] + ".py"
    try:
        # Load notebook
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # Convert to Python code
        exporter = PythonExporter()
        source_code, _ = exporter.from_notebook_node(nb)

        # Write converted Python code to .py file
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(source_code)

        #print(f"Detected Jupyter notebook: {notebook_path}")
        #print(f"Converting to Python file: {py_path}\n")
        styled_log(notebook_path, py_path)

    except Exception as e:
        print(f"[ERROR] Failed to convert {notebook_path}: {e}")

def styled_log(notebook_path, py_path):
    display(HTML(f"""
        <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; font-size: 11px;">
            <div><strong>Detected Jupyter notebook:</strong> <code>{notebook_path}</code></div>
            <div><strong>Converting to Python file:</strong> <code>{py_path}</code></div>
        </div>
    """))
