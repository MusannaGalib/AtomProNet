import os
import sys
import subprocess

def add_to_path(path):
    """Adds the given path to the user's PATH environment variable if it's not already there."""
    # Get current system PATH
    current_path = os.environ.get("PATH", "")
    
    # Check if the path is already in the PATH
    if path not in current_path:
        if sys.platform == "win32":
            # On Windows, use setx to permanently add the path to the user PATH variable
            subprocess.run(f'setx PATH "%PATH%;{path}"', shell=True)
            print(f"Added {path} to PATH.")
        elif sys.platform == "darwin" or sys.platform == "linux":
            # On macOS/Linux, modify .bashrc or .zshrc depending on the shell
            home_dir = os.path.expanduser("~")
            shell_config = os.path.join(home_dir, ".bashrc") if os.path.exists(os.path.join(home_dir, ".bashrc")) else os.path.join(home_dir, ".zshrc")
            if os.path.exists(shell_config):
                with open(shell_config, "a") as shell_file:
                    shell_file.write(f'\nexport PATH="{path}:$PATH"\n')
                print(f"Added {path} to {shell_config}.")
            else:
                print(f"Warning: No shell configuration file found at {shell_config}")
        else:
            print(f"Unsupported platform: {sys.platform}")

def get_executable_path():
    """Detects the executable's path, which should be in the Scripts folder."""
    if sys.platform == "win32":
        return os.path.expanduser(r"~\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts")
    else:
        # On macOS/Linux, this should be the user's local bin directory (can vary depending on how Python was installed)
        return os.path.expanduser("~/.local/bin")

if __name__ == "__main__":
    executable_path = get_executable_path()
    add_to_path(executable_path)
