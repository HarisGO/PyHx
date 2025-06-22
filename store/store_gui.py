# PyHx/store/store_gui.py

import subprocess
import requests
import platform
import json

def get_package_info_pip(package_name):
    """Gets information for a specific package from PyPI."""
    print(f"Checking PIP for '{package_name}'...")
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            info = data.get("info", {})
            return {
                "name": info.get("name"),
                "description": info.get("summary"),
                "version": info.get("version"),
                "source": "PIP"
            }
    except requests.RequestException:
        # This handles timeouts, connection errors, etc.
        pass
    return None

def get_package_info_apt(package_name):
    """Gets information for a specific package from apt."""
    # This function should only run on Linux systems.
    if platform.system() != "Linux":
        return None
        
    print(f"Checking APT for '{package_name}'...")
    try:
        cmd = ['apt-cache', 'show', package_name]
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        
        version, description = "N/A", "No description."
        for line in output.split('\n'):
            if line.startswith('Version:'):
                version = line.split(':', 1)[1].strip()
            if line.startswith('Description-en:'):
                description = line.split(':', 1)[1].strip()

        return {
            "name": package_name,
            "description": description,
            "version": version,
            "source": "APT"
        }
    except (FileNotFoundError, subprocess.CalledProcessError):
        # This catches if 'apt-cache' isn't found or the package doesn't exist.
        pass
    return None

def install_package(package):
    """Installs a selected package using the appropriate package manager."""
    source = package['source']
    name = package['name']
    
    print(f"\nInstalling '{name}' from {source}...")
    
    command = []
    if source == "APT":
        command = ['sudo', 'apt', 'install', '-y', name]
        print("APT packages require your main system password (sudo) to install.")
    elif source == "PIP":
        command = ['pip', 'install', name]

    try:
        # Stream the output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
        process.wait() # Wait for the command to complete
        
        if process.returncode == 0:
            print(f"\nSuccessfully installed '{name}'.")
        else:
            print(f"\nError: Installation of '{name}' failed.")

    except Exception as e:
        print(f"An unexpected error occurred during installation: {e}")

def main():
    """Main interactive loop for the PyHx App Store."""
    print("--- Welcome to the PyHx App Store ---")
    
    while True:
        try:
            package_name = input("\nEnter a specific package name to look up (or 'exit' to quit): ").strip()
            if not package_name:
                continue
            if package_name.lower() == 'exit':
                break

            found_packages = []
            
            # Check PIP
            pip_info = get_package_info_pip(package_name)
            if pip_info:
                found_packages.append(pip_info)
            
            # Check APT (only on Linux)
            apt_info = get_package_info_apt(package_name)
            if apt_info:
                found_packages.append(apt_info)

            if not found_packages:
                print(f"No package named '{package_name}' found in PIP or APT.")
                continue

            print("\n--- Found Packages ---")
            for i, pkg in enumerate(found_packages):
                print(f"{i+1}. [{pkg['source']}] {pkg['name']} (v{pkg['version']})\n"
                      f"     {pkg['description']}")
            print("----------------------")

            while True:
                choice_str = input("Enter the number to install, or 's' to search for another package: ").strip().lower()
                if choice_str == 's':
                    break
                
                try:
                    choice_int = int(choice_str) - 1
                    if 0 <= choice_int < len(found_packages):
                        install_package(found_packages[choice_int])
                        break
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input.")

        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nExiting the App Store. Goodbye!")

if __name__ == "__main__":
    main()
