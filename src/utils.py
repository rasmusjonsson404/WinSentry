import subprocess
import sys
import os
import ctypes
from termcolor import colored, cprint
from colorama import just_fix_windows_console

just_fix_windows_console()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_scheduled_task():
    # Adding WinSentry to autostart through task scheduler
    if not is_admin():
        cprint("ERROR: You must be admin to run installation", "red")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
    main_path = os.path.join(base_dir, "main.py")

    if not os.path.exists(venv_python):
        cprint(f"ERROR: Could not find .venv at: {venv_python}", "red")
        cprint("Please run Setup.bat first or check your folder structure.", "yellow")
        return
    
    task_name = "WinSentry"

    action_command = f'"{venv_python}" "{main_path}"'
    
    # Running command to add to task scheduler
    # /SC ONLOGON  = Run next login
    # /RL HIGHEST  = Run at highest privilege (Admin/Elevated)
    # /F           = Force
    # /TR          = Task Run
    
    check_command = ["schtasks", "/Create", "/TN", task_name, "/TR", action_command, "/SC", "ONLOGON", "/RL", "HIGHEST", "/F"]

    command = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", action_command,
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F"
    ]

    # Check if adding autostart succeeded
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            cprint(f"Success! WinSentry added to autostart.", "green")
            cprint(f"Using Python interpreter at: {venv_python}", "cyan")
        else:
            cprint(f"Did not manage to add to autostart: {result.stderr}", "red")
            
    except Exception as e:
        cprint(f"An error occurred at the installation: {e}", "red")

def uninstall_scheduled_task():
    if not is_admin():
        cprint("ERROR: You must be admin to run uninstallation", "red")
        return
    
    task_name = "WinSentry"

    # Check if task exist
    # "schtasks /Query" return 0 if it exist, 1 if missing.
    check_command = ["schtasks", "/Query", "/TN", task_name]
    
    check_result = subprocess.run(
        check_command, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

    # If task do not exist.
    if check_result.returncode != 0:
        cprint(f"Could not find any task with the name: '{task_name}'.", "yellow")
        return

    # If exist remove task.
    delete_command = ["schtasks", "/Delete", "/TN", task_name, "/F"]

    try:
        delete_result = subprocess.run(delete_command, capture_output=True, text=True)
        
        if delete_result.returncode == 0:
            cprint(f"Success! '{task_name}' has been removed from autostart.", "green")
        else:
            cprint(f"Critical error removing task: {delete_result.stderr.strip()}", "red")
            
    except Exception as e:
        cprint(f"An error occurred at uninstallation: {e}", "red")