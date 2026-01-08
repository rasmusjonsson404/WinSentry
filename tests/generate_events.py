import win32security
import win32con
import win32api
import time
import os
import sys
from termcolor import colored

try:
    import colorama
    colorama.init()
except ImportError:
    pass

def trigger_failed_login(count=1):
    """
    Attempts to log in with invalid credentials to trigger Windows Event ID 4625.
    """
    username = "WinSentryTestUser"
    domain = "."
    password = "ThisPasswordIsWrong123!"

    print(f"\n>> Generating {count} failed login attempts...")

    for i in range(count):
        try:
            # Attempt to logon
            handle = win32security.LogonUser(
                username,
                domain,
                password,
                win32con.LOGON32_LOGON_INTERACTIVE,
                win32con.LOGON32_PROVIDER_DEFAULT
            )
            win32api.CloseHandle(handle)
        except win32security.error:
            # We expect an error (Logon failure)
            print(colored(f"   [{i+1}/{count}] Generated Failed Login (Event 4625)", "red"))
        
        # Small delay to ensure timestamps differ slightly
        time.sleep(0.5)

if __name__ == "__main__":
    print("========================================")
    print("   WinSentry Event Generator (Test)")
    print("========================================")
    
    # Check if argument was passed via CLI (e.g. "python generate_events.py 10")
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            count = 5
    else:
        # If no argument, ASK the user
        user_input = input(">> How many failed logins to generate? (Default: 5): ")
        
        if user_input.strip() == "":
            count = 5
        else:
            try:
                count = int(user_input)
            except ValueError:
                print("Invalid number. Using default (5).")
                count = 5

    # Run the generator
    trigger_failed_login(count)

    print("\n>> Done! Check the WinSentry Dashboard now.")
    print(">> You should see a spike in the 'Attack Timeline'.")
    
    # Pause only if running via double-click (no arguments usually)
    if len(sys.argv) == 1:
        os.system("pause")