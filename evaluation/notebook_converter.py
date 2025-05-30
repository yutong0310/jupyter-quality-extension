import os
import nbformat
from nbconvert import PythonExporter

def convert_notebooks_in_dir(root_dir):
    """
    Converts all .ipynb notebooks under a directory (recursively) into .py Python files.

    This function modifies the folder in-place by generating .py files next to each .ipynb file. 
    These .py files will then be automatically picked up by the existing scanning logic in `evaluate_metrics()`.

    Args:
        root_dir (str): Path to the directory to recursively scan.
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".ipynb") and not file.startswith("."):
                notebook_path = os.path.join(dirpath, file)
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

                    print(f"Converted notebook to .py: {py_path}")

                except Exception as e:
                    print(f"[ERROR] Failed to convert {notebook_path}: {e}")
