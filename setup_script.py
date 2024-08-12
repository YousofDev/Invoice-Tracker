import os
import sys


def create_folders_and_files(prefixes):
    """
    Creates folders with plural names and files with singular names, avoiding overwrites.

    Args:
        prefixes (list): A list of strings representing prefixes for file names.
    """

    base_path = "."  # Replace with your desired base directory

    # Ensure base directory exists
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    main_folders = ["models", "repositories", "services", "schemas", "routers"]

    for prefix in prefixes:
        for folder in main_folders:
            folder_path = os.path.join(base_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Handle the special case of 'repository'
            if folder == "repositories":
                file_name = f"{prefix.lower()}_repository.py"
            else:
                file_name = f"{prefix.lower()}_{folder[:-1]}.py"

            file_path = os.path.join(folder_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    # Add template content here (optional)
                    f.write(f"")
            else:
                print(f"File '{file_path}' already exists.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_script.py prefix1 prefix2 ...")
        sys.exit(1)

    prefixes = sys.argv[1:]
    create_folders_and_files(prefixes)
