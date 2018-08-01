#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visual Studio Code envrionment manager

This module manages VS Code's extensions list and settings locally.
"""
import datetime
import difflib
import os
import pathlib
import subprocess
import sys

IS_WINDOWS = None

def man():
    """Show command line options"""
    print("Usage: {} [OPTION]".format(sys.argv[0]))
    print("""
OPTION
    backup     Backup extensions list to vscode-extension.txt
               and settings to vscode-settings.jsonc

    comp       Compare list between vscode-extensions.txt file and system
    install    Install extensions from vscode-extensions.txt
    uninstall  Uninstall extensions from vscode-extensions.txt

    diff       Compare vscode-settings.jsonc and system's settings.json
    restore    Restore vscode-settings.jsonc file to system's settings.json
""")

def backup():
    """Backup extensions list to `vscode-extension.txt` and settings to `vscode-settings.jsonc`"""
    # Backup extensions list to `vscode-extensions.txt``
    with open("vscode-extensions.txt", "w", encoding="utf-8", newline="\n") as file:
        subprocess.run(["code", "--list-extensions"], stdout=file, shell=IS_WINDOWS)

    # Backup settings file to `vscode-settings.jsonc`
    if sys.platform.startswith("linux"):
        subprocess.run(["cp ~/.config/Code/User/settings.json ./vscode-settings.jsonc"], shell=True)
    elif IS_WINDOWS:
        p = pathlib.Path(os.getenv("APPDATA")) / "Code" / "User" / "settings.json"
        subprocess.run("copy {} .\\vscode-settings.jsonc".format(p), shell=True)

def comp():
    """Compare extensions list between `vscode-extensions.txt` file and `system`"""
    with open("vscode-extensions.txt", "r") as file:
        # Get extensions list from the `vscode-extensions.txt` file
        extensions_file = [x.strip() for x in file.readlines()]

        # Get extensions list from a system
        args = ["code", "--list-extensions"]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=IS_WINDOWS)
        extensions_code = [x.decode("utf-8").strip() for x in p.stdout.readlines()]

        # Print extensions list in system but not in the file
        if set(extensions_code).difference(extensions_file):
            print("\n* CODE")
            print("-" * 40)
            for line in set(extensions_code).difference(extensions_file):
                print(line)

        # Print extensions list in the file but not in the system
        if set(extensions_file).difference(extensions_code):
            print("\n* FILE")
            print("-" * 40)
            for line in set(extensions_file).difference(extensions_code):
                print(line)

def install():
    """Install extensions from `vscode-extensions.txt`"""
    with open("vscode-extensions.txt", "r") as file:
        args = ["code", "--list-extensions"]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=IS_WINDOWS)
        extensions_code = [x.decode("utf-8").strip() for x in p.stdout.readlines()]
        extensions_file = [x.strip() for x in file.readlines()]

        for line in set(extensions_file).difference(extensions_code):
            subprocess.run(["code", "--install-extension", line], shell=IS_WINDOWS)

def uninstall():
    """Uninstall extensions from `vscode-extensions.txt`"""
    with open("vscode-extensions.txt", "r") as file:
        args = ["code", "--list-extensions"]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=IS_WINDOWS)
        extensions_code = [x.decode("utf-8").strip() for x in p.stdout.readlines()]
        extensions_file = [x.strip() for x in file.readlines()]

        for line in set(extensions_code).difference(extensions_file):
            subprocess.run(["code", "--uninstall-extension", line], shell=IS_WINDOWS)

def diff():
    """Compare `vscode-settings.jsonc` and system's `settings.json`"""
    with open("vscode-settings.jsonc", "r") as file_backup:
        # Get system's `settings.json` file path
        if sys.platform.startswith("linux"):
            p = pathlib.Path("~/.config/Code/User/settings.json")
        elif IS_WINDOWS:
            p = pathlib.Path(os.getenv("APPDATA")) / "Code" / "User" / "settings.json"

        with p.expanduser().open("r") as file_system:
            sys.stdout.writelines(
                difflib.unified_diff(file_backup.readlines(), file_system.readlines()
                    , "before.json", "after.json")
            )

def restore():
    """Restore `vscode-settings.jsonc` file to system's `settings.json`"""
    # Get system's `settings.json` file path
    if sys.platform.startswith("linux"):
        p = pathlib.Path("~/.config/Code/User/settings.json")
    elif IS_WINDOWS:
        p = pathlib.Path(os.getenv("APPDATA")) / "Code" / "User" / "settings.json"

    # Backup the system setting file to `vscode-settings-[CURRENT_TIME].jsonc` before restore
    with p.expanduser().open("r") as file_system \
            , open("vscode-settings-" + str(int(datetime.datetime.now().timestamp())) + ".jsonc"
                    , "w", encoding="utf-8", newline="\n") as file_backup:
        file_backup.write(file_system.read())

    # Restore the `vscode-settings.jsonc` file to system
    with open("vscode-settings.jsonc", "r") as file_to_restore, \
                open(p, "w", encoding="utf-8", newline="\n") as file_system:
        file_system.write(file_to_restore.read())

FUNCTIONS = {
    'backup': backup,
    'diff': diff,
    'comp': comp,
    'restore': restore,
    'install': install,
    'uninstall': uninstall
}

if __name__ == "__main__":
    if sys.platform.startswith("linux"):
        IS_WINDOWS = False
    elif sys.platform.startswith("win32"):
        IS_WINDOWS = True

    if len(sys.argv) == 2 and sys.argv[1] in FUNCTIONS.keys():
        FUNCTIONS[sys.argv[1]]()
    else:
        man()
