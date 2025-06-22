# PyHx/main.py

import os
import getpass
import time
import shutil
import subprocess
import tempfile
import sys
import json
import hashlib
import datetime
import platform
import random
import re
import calendar
import base64
import binascii

# --- Global State ---
COMMAND_HISTORY = []

# --- Configuration and Constants ---
# Using local directories as per the restored design
CONFIG_DIR = "config"
PACKAGES_DIR = "packages"
INSTALLED_DIR = os.path.join(PACKAGES_DIR, "installed")
HOSTNAME_FILE = os.path.join(CONFIG_DIR, "hostname.txt")
USERS_FILE = os.path.join(CONFIG_DIR, "users.json")
START_TIME = time.time()

# --- User and Auth Helper Functions ---
def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_users():
    """Loads user data from the JSON file or creates a default root user."""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupt, create a default root user
        print("First run detected or users.json is invalid. Creating default 'root' user.")
        print("Default password is 'root'. Please change it immediately with 'changepass'.")
        default_users = {"root": {"password": hash_password("root"), "role": "admin"}}
        save_users(default_users)
        return default_users

def save_users(users_data):
    """Saves user data to the JSON file."""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=4)

def get_hostname():
    """Reads the hostname from its file or returns a default."""
    try:
        with open(HOSTNAME_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except (FileNotFoundError, UnicodeDecodeError):
        # Create a default hostname file if it doesn't exist
        default_hostname = "pyhx-host"
        with open(HOSTNAME_FILE, 'w', encoding='utf-8') as f:
            f.write(default_hostname)
        return default_hostname

# --- BACKEND COMMAND LOGIC ---
def _sysinfo_logic(args, user):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
    print(f"PyHx Version: 2.3.0 'Hybrid'")
    print(f"Hostname:     {get_hostname()}")
    print(f"Uptime:       {uptime_str}")
    print(f"User:         {user['name']} (Role: {user['role']})")
    print(f"Location:     {os.getcwd()}")
    return True, user

def _help_logic(args, user):
    if not args:
        print("PyHx OS - Friendly Command List. For details, type 'help <command>'.")
        categories = {"System": [], "File": [], "User": [], "App": [], "Tools": []}
        for cmd in sorted(COMMANDS.keys()):
            cat = COMMANDS[cmd].get('category', 'Tools')
            categories[cat].append(cmd)
        for cat, cmds in categories.items():
            print(f"\n--- {cat} Commands ---")
            for cmd_name in cmds:
                print(f"  {cmd_name:<12} {COMMANDS[cmd_name]['help']}")
    else:
        cmd_to_help = args[0]
        if cmd_to_help in COMMANDS:
            print(f"{cmd_to_help}: {COMMANDS[cmd_to_help]['help']}")
        else:
            print(f"Error: Command '{cmd_to_help}' not found.")
    return True, user

def _clear_logic(args, user):
    os.system('cls' if os.name == 'nt' else 'clear')
    return True, user

def _history_logic(args, user):
    for i, cmd in enumerate(COMMAND_HISTORY):
        print(f"{i+1:3d}  {cmd}")
    return True, user

def _datetime_logic(args, user):
    print(datetime.datetime.now().strftime("%A, %d %B %Y - %H:%M:%S"))
    return True, user

def _restart_logic(args, user):
    print("Restarting PyHx shell...")
    os.execv(sys.executable, ['python'] + sys.argv)
    return False, user

def _whoami_logic(args, user):
    print(user['name'])
    return True, user

def _version_logic(args, user):
    print("PyHx OS Version: 2.3.0 'Hybrid'")
    return True, user

def _pwd_logic(args, user):
    print(os.getcwd())
    return True, user

def _cd_logic(args, user):
    if not args:
        print("Usage: go <directory>")
        return True, user
    try:
        os.chdir(args[0])
    except FileNotFoundError:
        print(f"Error: Directory '{args[0]}' not found.")
    except Exception as e:
        print(f"Error: Could not change directory. {e}")
    return True, user

def _ls_logic(args, user):
    path = args[0] if args else "."
    try:
        files = os.listdir(path)
        if not files:
            print(f"Directory '{path}' is empty.")
        for f in sorted(files, key=str.lower):
            is_dir = os.path.isdir(os.path.join(path, f))
            print(f"{'[DIR] ' if is_dir else '      '}{f}")
    except FileNotFoundError:
        print(f"Error: Directory '{path}' not found.")
    return True, user

def _make_logic(args, user):
    if len(args) < 2:
        print("Usage: make <file|dir> <name>")
        return True, user
    make_type, name = args[0], " ".join(args[1:])
    if make_type == 'file':
        try:
            with open(name, 'a'):
                os.utime(name, None)
            print(f"File '{name}' created.")
        except Exception as e:
            print(f"Error creating file: {e}")
    elif make_type == 'dir':
        try:
            os.makedirs(name)
            print(f"Directory '{name}' created.")
        except FileExistsError:
            print(f"Error: Directory '{name}' already exists.")
        except Exception as e:
            print(f"Error: Could not create directory. {e}")
    else:
        print("Usage: make <file|dir> <name>")
    return True, user

def _read_logic(args, user):
    if not args:
        print("Usage: read <filename>")
        return True, user
    try:
        with open(args[0], 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"Error: File '{args[0]}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")
    return True, user

def _delete_logic(args, user):
    if not args:
        print("Usage: delete <file_or_empty_dir>")
        return True, user
    target = args[0]
    try:
        confirmation = input(f"Are you sure you want to delete '{target}'? (y/n): ")
        if confirmation.lower() != 'y':
            print("Deletion cancelled.")
            return True, user
        if os.path.isdir(target):
            os.rmdir(target)
            print(f"Directory '{target}' deleted.")
        else:
            os.remove(target)
            print(f"File '{target}' deleted.")
    except FileNotFoundError:
        print(f"Error: '{target}' not found.")
    except OSError:
        print(f"Error: Directory '{target}' is not empty.")
    except Exception as e:
        print(f"Error deleting: {e}")
    return True, user

def _copy_logic(args, user):
    if len(args) != 2:
        print("Usage: copy <source> <destination>")
        return True, user
    try:
        shutil.copy(args[0], args[1])
        print(f"Copied '{args[0]}' to '{args[1]}'.")
    except Exception as e:
        print(f"Error copying file: {e}")
    return True, user

def _move_logic(args, user):
    if len(args) != 2:
        print("Usage: move <source> <destination>")
        return True, user
    try:
        shutil.move(args[0], args[1])
        print(f"Moved '{args[0]}' to '{args[1]}'.")
    except Exception as e:
        print(f"Error moving file: {e}")
    return True, user

def _say_logic(args, user, outfile=None, append=False):
    output = " ".join(args)
    if outfile:
        try:
            with open(outfile, 'a' if append else 'w', encoding='utf-8') as f:
                f.write(output + '\n')
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print(output)
    return True, user

def _count_logic(args, user):
    if not args:
        print("Usage: count <filename>")
        return True, user
    try:
        lines, words, chars = 0, 0, 0
        with open(args[0], 'r', encoding='utf-8') as f:
            for line in f:
                lines += 1
                words += len(line.split())
                chars += len(line)
        print(f"Lines: {lines}, Words: {words}, Chars: {chars} --- {args[0]}")
    except FileNotFoundError:
        print(f"Error: File '{args[0]}' not found.")
    return True, user

def _findtext_logic(args, user):
    if len(args) < 2:
        print("Usage: findtext <pattern> <filename>")
        return True, user
    pattern, filename = args[0], args[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if re.search(pattern, line, re.IGNORECASE):
                    print(f"{i+1}:{line.strip()}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return True, user

def _changepass_logic(args, user):
    print(f"Changing password for {user['name']}.")
    users = load_users()
    current_pass = getpass.getpass("Current password: ")
    if hash_password(current_pass) != users[user['name']]['password']:
        print("Authentication failed.")
        return True, user
    new_pass = getpass.getpass("New password: ")
    if new_pass != getpass.getpass("Confirm new password: "):
        print("Passwords do not match.")
        return True, user
    users[user['name']]['password'] = hash_password(new_pass)
    save_users(users)
    print("Password changed successfully.")
    return True, user

def _switchuser_logic(args, user):
    print("Switching user...")
    new_user = authenticate(is_su=True)
    if new_user:
        return True, new_user
    else:
        print("Switch user failed. Returning to current session.")
        return True, user

def _calc_logic(args, user):
    if not args:
        print("Usage: calc <expression>")
        return True, user
    expression = "".join(args)
    if not re.match(r"^[0-9+\-*/.() ]+$", expression):
        print("Error: Invalid characters in expression.")
        return True, user
    try:
        print(eval(expression))
    except Exception as e:
        print(f"Error: {e}")
    return True, user

def _calendar_logic(args, user):
    print(calendar.month(datetime.datetime.now().year, datetime.datetime.now().month))
    return True, user

def _roll_logic(args, user):
    print(f"You rolled a {random.randint(1, 6)}.")
    return True, user

def _cowsay_logic(args, user):
    text = " ".join(args) if args else "Moo!"
    print(" " + "_" * (len(text) + 2))
    print(f"< {text} >")
    print(" " + "-" * (len(text) + 2))
    print(r"        \   ^__^")
    print(r"         \  (oo)\_______")
    print(r"            (__)\       )\/\\")
    print(r"                ||----w |")
    print(r"                ||     ||")
    return True, user

def _joke_logic(args, user):
    try:
        import requests
        res = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5).json()
        print(f"Q: {res['setup']}")
        time.sleep(2)
        print(f"A: {res['punchline']}")
    except Exception:
        print("Could not fetch a joke. The internet must be sad today.")
    return True, user

def _user_logic(args, user):
    if user['role'] != 'admin':
        print("Error: Permission denied.")
        return True, user
    if not args or args[0] not in ['add', 'delete']:
        print("Usage: user <add|delete> ...")
        return True, user
    sub_command, sub_args = args[0], args[1:]
    if sub_command == "add":
        if len(sub_args) != 3 or sub_args[0] not in ['-u', '-a']:
            print("Usage: user add <-u|-a> <username> <password>")
            return True, user
        flag, username, password = sub_args
        role = 'user' if flag == '-u' else 'admin'
        users = load_users()
        if username in users:
            print(f"Error: User '{username}' already exists.")
            return True, user
        users[username] = {"password": hash_password(password), "role": role}
        save_users(users)
        print(f"Successfully added user '{username}' with role '{role}'.")
    elif sub_command == "delete":
        if len(sub_args) != 1:
            print("Usage: user delete <username>")
            return True, user
        username_to_delete = sub_args[0]
        users = load_users()
        if username_to_delete not in users:
            print(f"Error: User '{username_to_delete}' not found.")
            return True, user
        if username_to_delete == 'root':
            print("Error: The 'root' user cannot be deleted.")
            return True, user
        if username_to_delete == user['name']:
            print("Error: You cannot delete yourself.")
            return True, user
        confirmation = input(f"To confirm deletion of '{username_to_delete}', please type the username again: ")
        if confirmation != username_to_delete:
            print("Confirmation failed.")
            return True, user
        del users[username_to_delete]
        save_users(users)
        print(f"Successfully deleted user '{username_to_delete}'.")
    return True, user

def _net_logic(args, user):
    if not args or args[0] not in ['ping', 'lookup', 'get']:
        print("Usage: net <ping|lookup|get> ...")
        return True, user
    sub_command, sub_args = args[0], args[1:]
    if sub_command == 'ping':
        if not sub_args:
            print("Usage: net ping <host>")
            return True, user
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', sub_args[0]]
        try:
            subprocess.run(command)
        except FileNotFoundError:
            print("Error: 'ping' command not found.")
    elif sub_command == 'lookup':
        if not sub_args:
            print("Usage: net lookup <host>")
            return True, user
        try:
            subprocess.run(['nslookup', sub_args[0]])
        except FileNotFoundError:
            print("Error: 'nslookup' command not found.")
    elif sub_command == 'get':
        if not sub_args:
            print("Usage: net get <URL>")
            return True, user
        try:
            import requests
            response = requests.get(sub_args[0], timeout=10)
            print(response.text)
        except ImportError:
            print("Error: 'requests' library not installed.")
        except Exception as e:
            print(f"Error fetching URL: {e}")
    return True, user

# --- RESTORED APP COMMANDS ---
def convert_command(args, user):
    if len(args) != 2 or args[0] != '-pyhx':
        print("Usage: convert -pyhx <folder_name>")
        return True, user
    folder = args[1]
    script = os.path.join('tools', 'pyhx_converter.py')
    print(f"Invoking converter for '{folder}'...")
    try:
        subprocess.run([sys.executable, script, folder], check=True)
    except FileNotFoundError:
        print("Error: Converter script not found. Make sure 'tools/pyhx_converter.py' exists.")
    except Exception:
        print("Error during conversion process.")
    return True, user

def install_command(args, user):
    if not args:
        print("Usage: install <package.pyhx>")
        return True, user
    pkg_name = args[0]
    src = os.path.join(PACKAGES_DIR, pkg_name)
    dst = os.path.join(INSTALLED_DIR, pkg_name)
    if not os.path.exists(src):
        print(f"Error: Package '{pkg_name}' not found in staging area ('{PACKAGES_DIR}').")
        return True, user
    try:
        shutil.move(src, dst)
        print(f"Successfully installed '{pkg_name}'.")
    except Exception as e:
        print(f"Error during installation: {e}")
    return True, user

def run_command(args, user):
    if not args:
        print("Usage: run <package.pyhx>")
        return True, user
    pkg_name = args[0]
    pkg_path = os.path.join(INSTALLED_DIR, pkg_name)
    if not os.path.exists(pkg_path):
        print(f"Error: Package '{pkg_name}' is not installed.")
        return True, user
    temp_dir = tempfile.mkdtemp(prefix="pyhx_run_")
    try:
        shutil.unpack_archive(pkg_path, temp_dir, 'zip')
        entry_point = os.path.join(temp_dir, 'main.py')
        if not os.path.exists(entry_point):
            print(f"Error: 'main.py' not found in package '{pkg_name}'.")
            return True, user
        print(f"\n--- Running {pkg_name} ---")
        subprocess.run([sys.executable, 'main.py'], cwd=temp_dir)
        print(f"--- {pkg_name} finished ---\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        shutil.rmtree(temp_dir)
    return True, user

def store_gui_command(args, user):
    script = os.path.join('store', 'store_gui.py')
    print("Launching App Store...")
    try:
        subprocess.run([sys.executable, script])
    except FileNotFoundError:
        print("Error: App Store script not found. Make sure 'store/store_gui.py' exists.")
    except Exception as e:
        print(f"Error launching the store: {e}")
    return True, user

def h7t_command(args, user):
    return run_command(['H7T.pyhx'], user)

# --- COMMAND DICTIONARY ---
COMMANDS = {
    # System
    "help": {"func": _help_logic, "help": "Displays the command list.", "category": "System"},
    "info": {"func": _sysinfo_logic, "help": "Shows system and user information.", "category": "System"},
    "clear": {"func": _clear_logic, "help": "Clears the screen.", "category": "System"},
    "history": {"func": _history_logic, "help": "Shows command history for this session.", "category": "System"},
    "datetime": {"func": _datetime_logic, "help": "Displays the current date and time.", "category": "System"},
    "restart": {"func": _restart_logic, "help": "Restarts the PyHx shell.", "category": "System"},
    "shutdown": {"func": (lambda a, u: (False, u)), "help": "Exits the PyHx shell.", "category": "System"},
    "version": {"func": _version_logic, "help": "Shows the PyHx OS version.", "category": "System"},
    # File
    "whereami": {"func": _pwd_logic, "help": "Tells you your current directory.", "category": "File"},
    "go": {"func": _cd_logic, "help": "Go to a different directory.", "category": "File"},
    "look": {"func": _ls_logic, "help": "Look at the files in a directory.", "category": "File"},
    "make": {"func": _make_logic, "help": "Make a 'file' or 'dir'.", "category": "File"},
    "read": {"func": _read_logic, "help": "Read the contents of a file.", "category": "File"},
    "delete": {"func": _delete_logic, "help": "Delete a file or empty directory.", "category": "File"},
    "copy": {"func": _copy_logic, "help": "Copy a file.", "category": "File"},
    "move": {"func": _move_logic, "help": "Move or rename a file.", "category": "File"},
    "say": {"func": _say_logic, "help": 'Prints text. Use > to make a file (e.g., say "hi" > a.txt).', "category": "File"},
    "count": {"func": _count_logic, "help": "Count lines, words, and characters in a file.", "category": "File"},
    "findtext": {"func": _findtext_logic, "help": "Find text inside a file.", "category": "File"},
    # User
    "whoami": {"func": _whoami_logic, "help": "Displays your username.", "category": "User"},
    "user": {"func": _user_logic, "help": "Manages users (add, delete). Admin only.", "category": "User"},
    "changepass": {"func": _changepass_logic, "help": "Change your password.", "category": "User"},
    "switchuser": {"func": _switchuser_logic, "help": "Switch to another user account.", "category": "User"},
    # App
    "convert": {"func": convert_command, "help": "Converts a folder to a .pyhx package (e.g. convert -pyhx <folder>).", "category": "App"},
    "install": {"func": install_command, "help": "Installs a .pyhx package from the staging area.", "category": "App"},
    "run": {"func": run_command, "help": "Runs an installed .pyhx package.", "category": "App"},
    "store-gui": {"func": store_gui_command, "help": "Opens the App Store to find new packages.", "category": "App"},
    "h7t": {"func": h7t_command, "help": "Shortcut to run the H7T app.", "category": "App"},
    # Tools
    "net": {"func": _net_logic, "help": "Network tools (ping, lookup, get).", "category": "Tools"},
    "calc": {"func": _calc_logic, "help": "A simple calculator.", "category": "Tools"},
    "calendar": {"func": _calendar_logic, "help": "Displays a calendar for the current month.", "category": "Tools"},
    "roll": {"func": _roll_logic, "help": "Rolls a six-sided die.", "category": "Tools"},
    "cowsay": {"func": _cowsay_logic, "help": "An ASCII cow says your message.", "category": "Tools"},
    "joke": {"func": _joke_logic, "help": "Tells a random programming joke.", "category": "Tools"},
}

# --- Main Application Logic ---
def ensure_dirs_exist():
    """Ensures all necessary local directories exist at startup."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    os.makedirs(INSTALLED_DIR, exist_ok=True)

def authenticate(is_su=False):
    """Handles the user selection and login process."""
    if not is_su:
        print("--- Welcome to PyHx OS ---")
    users = load_users()
    user_list = list(users.keys())
    print("Please select a user:")
    for i, username in enumerate(user_list):
        print(f"  {i+1}. {username}")
    try:
        choice = int(input("Enter number: ")) - 1
        if not 0 <= choice < len(user_list):
            print("Invalid selection.")
            return None
        username = user_list[choice]
        password = getpass.getpass(f"Password for {username}: ")
        if hash_password(password) == users[username]['password']:
            if not is_su:
                print(f"\nLogin successful. Welcome, {username}!")
            return {"name": username, "role": users[username]['role']}
        else:
            print("\nAuthentication failed.")
            return None
    except (ValueError, IndexError):
        print("Invalid input.")
        return None

def parse_input(raw_input_str):
    """New parser to handle I/O redirection."""
    outfile, append = None, False
    if '>>' in raw_input_str:
        parts = raw_input_str.split('>>', 1)
        args_part, outfile = parts[0].strip(), parts[1].strip()
        append = True
    elif '>' in raw_input_str:
        parts = raw_input_str.split('>', 1)
        args_part, outfile = parts[0].strip(), parts[1].strip()
    else:
        args_part = raw_input_str
    
    parts = args_part.split()
    command = parts[0].lower() if parts else ''
    args = parts[1:]
    return command, args, outfile, append

def main():
    """The main entry point and shell loop."""
    ensure_dirs_exist()
    current_user = authenticate()
    if not current_user:
        return
    running = True
    while running:
        prompt = f"{current_user['name']}@{get_hostname()}:{os.path.basename(os.getcwd())}$ "
        try:
            raw_input_str = input(prompt)
            if not raw_input_str:
                continue
            COMMAND_HISTORY.append(raw_input_str)
            command, args, outfile, append = parse_input(raw_input_str)
            if command in COMMANDS:
                if command == 'say':
                    running, current_user = COMMANDS[command]['func'](args, current_user, outfile, append)
                else:
                    if outfile:
                        print("Error: Redirection `>` is only supported for the 'say' command.")
                    running, current_user = COMMANDS[command]['func'](args, current_user)
            else:
                print(f"PyHx: command not found: {command}")
        except (KeyboardInterrupt, EOFError):
            print("\nUse 'shutdown' to exit.")
            break

if __name__ == "__main__":
    # Set working directory to the script's location for consistency
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    main()
