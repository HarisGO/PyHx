# PyHx OS
A terminal-based pseudo-operating system written entirely in Python. PyHx emulates a minimal OS-like environment with a custom shell, multi-user support, a sandboxed application format, and an intuitive, human-readable command language for core tasks.

## 🔥 Why PyHx?
PyHx is built with **usability first**. It's designed to be a fun, hackable, and educational project for both beginners and power users.

* **Human-Readable Commands**: No need to memorize cryptic commands for file management. Instead of `ls` or `mkdir`, you use `look` and `make dir`.
* **Sandboxed App System**: A complete `.pyhx` application system lets you package, install, and run custom terminal apps in a safe, isolated environment.
* **Multi-User Support**: A complete user system with `admin` and `user` roles, password hashing, and privileged commands.
* **Built-in Tools**: Comes with a rich set of commands for system info, user management, network tools, and more.

## 🚀 Getting Started

### Prerequisites
* Python 3.9 or higher.
* `pip` (Python's package installer).
* `git` for cloning the repository.

### Installation & First Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/HarisGO/PyHx.git](https://github.com/HarisGO/PyHx.git)
    ```

2.  **Navigate into the project directory:**
    ```bash
    cd PyHx
    ```
    
3.  **Run PyHx:**
    ```bash
    python main.py
    ```

On the very first run, PyHx automatically creates the necessary `config` and `packages` folders inside your project directory. The default administrator account `root` is created with the password `root`. It is highly recommended to log in and immediately change this password using the `changepass` command.

## 💻 How to Use PyHx
After starting `python main.py`, you'll be greeted by the user selection menu. Choose your user and enter your password to log in.

The prompt shows your current username, hostname, and directory, ready for your commands:
`root@pyhx-host:PyHx$`

To see a full list of commands and what they do, just type `help`.

## 📦 The `.pyhx` App System
PyHx features a custom application format, `.pyhx`, for running sandboxed programs. A `.pyhx` file is simply a ZIP archive containing the app's code, with a `main.py` file at its root.

This allows you to create and share your own terminal applications that can be safely run within PyHx.

### Example: Creating and Running a "Hello World" App

1.  **Create your app's folder and file:**
    ```
    my-app/
    └── main.py
    ```

2.  **Write your Python code** in `my-app/main.py`:
    ```python
    # my-app/main.py
    name = input("What's your name? ")
    print(f"Hello, {name}, from inside a PyHx app!")
    ```

3.  **Launch PyHx** and use the `convert` command to package your app. This creates `my-app.pyhx` in the `packages/` staging folder.
    ```
    PyHx$ convert -pyhx my-app-dir
    ```

4.  **Install the app** to make it runnable. This moves it to the `packages/installed/` directory.
    ```
    install my-app.pyhx
    ```

5.  **Run your app!**
    ```
    run my-app.pyhx
    ```
    The OS will launch your app in a safe, temporary environment and clean up automatically when it's done.

## 📝 Command Reference
PyHx uses a simple, verb-based command language for most file and system operations, and standard names for its unique features.

### System Commands
| Command | Description |
| :--- | :--- |
| `help` | Displays the command list and details for specific commands. |
| `info` | Shows system, user, and version information. |
| `history` | Shows the commands used in the current session. |
| `clear` | Clears the terminal screen. |
| `datetime` | Displays the current date and time. |
| `restart` | Restarts the PyHx shell. |
| `shutdown` | Exits PyHx. |

### File & Directory Commands
| Command | Example Usage | Description |
| :--- | :--- | :--- |
| `look` | `look` or `look subfolder` | Look at the files in a directory. |
| `go` | `go subfolder` | Go to a different directory. |
| `whereami`| `whereami` | Tells you your current directory path. |
| `make` | `make file notes.txt` | Make a new `file` or `dir`. |
| `read` | `read notes.txt` | Read the contents of a file. |
| `delete` | `delete notes.txt` | Delete a file or empty directory (with confirmation). |
| `copy` | `copy a.txt b.txt` | Copy a file. |
| `move` | `move a.txt projects/` | Move or rename a file or directory. |
| `say` | `say "Hi" > hello.txt` | Prints text or writes/appends (`>>`) it to a file. |
| `count` | `count notes.txt` | Count lines, words, and characters in a file. |
| `findtext`| `findtext "Error" log.txt` | Find text inside a file (case-insensitive). |

### User Commands
| Command | Example Usage | Description |
| :--- | :--- | :--- |
| `whoami` | `whoami` | Displays your current username. |
| `user` | `user add -u bob 123` | Manages users (`add`, `delete`). Admin only. |
| `changepass`| `changepass` | Change your own password. |
| `switchuser`| `switchuser` | Switch to another user account. |

### Application Commands
| Command | Example Usage | Description |
| :--- | :--- | :--- |
| `store-gui` | `store-gui` | Opens the App Store to find `pip`/`apt` packages. |
| `convert` | `convert -pyhx my-app`| Packages a folder into a `.pyhx` file. |
| `install` | `install my-app.pyhx`| Installs a packaged app. |
| `run` | `run my-app.pyhx` | Runs an installed app in a sandbox. |
| `h7t` | `h7t` | A shortcut to run the pre-installed Hacker Toolkit. |
| In The New Update, add app before these commands for it to work |

### Tools & Fun
| Command | Example Usage | Description |
| :--- | :--- | :--- |
| `net` | `net ping google.com` | Network tools (`ping`, `lookup`, `get`). |
| `calc` | `calc 100 / 5` | A simple calculator for math expressions. |
| `calendar`| `calendar` | Displays a calendar for the current month. |
| `roll dice`| `roll dice` | Rolls a six-sided die. |
| `cowsay` | `cowsay Hello World` | An ASCII cow says your message. |
| `joke` | `joke` | Tells a random programming joke. |

## 📁 Directory Structure
The PyHx project is organized to be modular and easy to navigate.
