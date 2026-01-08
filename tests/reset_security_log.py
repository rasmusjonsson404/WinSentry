import os
import sys
import ctypes
import time
from termcolor import colored
import logger

try:
    import colorama
    colorama.init()
except ImportError:
    pass

def is_admin():
    """Checks if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def clear_security_log():
    print("========================================")
    print("   WinSentry: Reset Security Log")
    print("========================================")
    print(colored("WARNING: This will clear the ENTIRE Windows Security Log.", "yellow"))
    print("This resets the 'Total Failures' counter in WinSentry to 0.")
    print("The whole security history in Windows will be lost.")
    print("")

    if not is_admin():
        print(colored("[CRITICAL] This script requires Administrator privileges.", "red"))
        print("Please run the terminal or Run.bat as Administrator.")
        return

    confirm = input("Are you sure you want to proceed? (Y/N): ")
    
    if confirm.upper() == "Y":
        logger.info("User confirmed to delete windows security logs.")
        print("\n>> Clearing Windows Security Log...")
        result = os.system("wevtutil cl Security")
        
        if result == 0:
            logger.info("Windows security logs deleted by user.")
            print(colored(">> Success! Security Log has been reset to 0.", "green"))
            print(">> If you restart WinSentry now, the counter will be 0.")
        else:
            logger.info("Program did not manage to delete Windows security logs.")
            print(colored(f">> Failed to clear log. Error code: {result}", "red"))
    else:
        logger.info("Clearing Windows security logs cancelled.")
        print("Operation cancelled.")

if __name__ == "__main__":
    clear_security_log()
    
    if len(sys.argv) == 1:
        print("")
        os.system("pause")