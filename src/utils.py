import subprocess
import sys
import os
import ctypes
from termcolor import colored, cprint
from colorama import just_fix_windows_console
import logging

just_fix_windows_console()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def stop_scheduled_task():
    """Stops the running instance of WinSentry if it was started by Task Scheduler."""
    if not is_admin():
        cprint("ERROR: Admin privileges required to stop the background service.", "red")
        return

    task_name = "WinSentry"
    print(f">> Attempting to stop background service '{task_name}'...")

    # /End stops the task instance immediately
    command = ["schtasks", "/End", "/TN", task_name]
    
    # We capture output to avoid ugly error messages if it wasn't running
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        cprint("Success! The background service has been stopped.", "green")
        logging.info("User manually stopped the background service via menu.")
    else:
        # Common error: The task is not currently running.
        cprint("Service was not running (or could not be stopped).", "yellow")

def install_scheduled_task():
    # Adding WinSentry to autostart through task scheduler
    if not is_admin():
        cprint("ERROR: You must be admin to run installation", "red")
        logging.info("Failed to add to startup: No admin privileges.")
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
    
    # /SC ONSTART = Run at boot (Hidden/Background)
    command = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", action_command,
        "/SC", "ONSTART",
        "/RL", "HIGHEST",
        "/F"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            cprint(f"Success! WinSentry added to autostart (System Startup).", "green")
            cprint("The program will now start automatically when the computer turns on.", "cyan")
            logging.info("Successfully added program to windows startup.")
        else:
            cprint(f"Failed to add task: {result.stderr}", "red")
            logging.error(f"Failed to add task: {result.stderr}")
            
    except Exception as e:
        cprint(f"An error occurred: {e}", "red")
        logging.error(f"Error during installation: {e}")

def uninstall_scheduled_task():
    if not is_admin():
        cprint("ERROR: You must be admin to run uninstallation", "red")
        return
    
    task_name = "WinSentry"

    # STOP the task first (New functionality)
    stop_scheduled_task()

    # Check if task exists
    check_command = ["schtasks", "/Query", "/TN", task_name]
    check_result = subprocess.run(check_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if check_result.returncode != 0:
        cprint(f"Could not find any task with the name: '{task_name}'.", "yellow")
        return

    # Delete the task
    delete_command = ["schtasks", "/Delete", "/TN", task_name, "/F"]

    try:
        delete_result = subprocess.run(delete_command, capture_output=True, text=True)
        
        if delete_result.returncode == 0:
            cprint(f"Success! '{task_name}' has been removed from autostart.", "green")
            logging.info("Program removed from windows startup.")
        else:
            cprint(f"Error removing task: {delete_result.stderr.strip()}", "red")
            
    except Exception as e:
        cprint(f"An error occurred: {e}", "red")