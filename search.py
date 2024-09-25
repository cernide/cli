import os
import ast

# Step 1: List all Python files in the project


def list_all_python_files(root_dir):
    python_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(os.path.relpath(full_path, root_dir))
    return set(python_files)

# Step 2: Find all referenced files by walking through imports


def find_imported_files(root_dir):
    imported_files = set()
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                with open(full_path, 'r') as f:
                    try:
                        tree = ast.parse(f.read(), filename=full_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                                for alias in node.names:
                                    module_path = alias.name.replace(
                                        '.', '/') + '.py'
                                    imported_files.add(module_path)
                    except SyntaxError:
                        pass  # Skip files with syntax errors
    return imported_files

# Step 3: Find unused files


def find_unused_files(root_dir):
    all_files = list_all_python_files(root_dir)
    imported_files = find_imported_files(root_dir)
    unused_files = all_files - imported_files
    return unused_files


# Usage
if __name__ == "__main__":
    # Change this to your project directory
    project_directory = "/Users/rroper/Developer/cernide/cli/cli"
    unused_files = find_unused_files(project_directory)

    if unused_files:
        print("Unused files:")
        for file in unused_files:
            print(file)
    else:
        print("No unused files found!")
