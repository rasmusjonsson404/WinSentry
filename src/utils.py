import subprocess
import sys
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_scheduled_task():
    # Adding WinSentry to autostart through task scheduler
    if not is_admin():
        print("ERROR: You must be admin to run installation")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_path = os.path.join(base_dir, "main.py")
    
    task_name = "WinSentry"
    
    # Running command to add to task scheduler
    # /SC ONLOGON  = Run next login
    # /RL HIGHEST  = Run at highest privilege (Admin/Elevated)
    # /F           = Force
    # /TR          = Task Run
    
    command = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", f'"{main_path}"',
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F"
    ]

    # Check if adding autostart succeeded
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Success! WinSentry added to autostart.")
            print("Named 'WinSentry' in scheduler.")
        else:
            print(f"Did not manage to add to autostart: {result.stderr}")
            
    except Exception as e:
        print(f"An error occurred at the installation: {e}")