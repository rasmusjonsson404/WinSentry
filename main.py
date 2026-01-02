import sys
import platform
import argparse
from termcolor import colored, cprint
from src import utils
from colorama import just_fix_windows_console

just_fix_windows_console()

def main():

    parser = argparse.ArgumentParser(
        description="WinSentry: Windows Security Log Analyzer & Visualizer",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="WinSentry v0.0.3",
        help="Show program version and exit."
    )

    parser.add_argument(
        "-a", "--autostart",
        action="store_true",
        help="Add WinSentry to Windows Task Scheduler (Requires Admin)."
    )

    parser.add_argument(
        "-u", "--unautostart",
        action="store_true",
        help="Remove WinSentry from Windows Task Scheduler (Requires Admin)."
    )

    # This line reads sys.argv and matches it against rules above.
    # If -h is used, it prints help and exits here.
    args = parser.parse_args()

    if args.autostart:
        print(">> Mode: Installation of autostart")
        utils.install_scheduled_task()

    elif args.unautostart:
        print(">> Mode: Uninstallation of autostart")
        utils.uninstall_scheduled_task()
        
    elif args.dashboard:
        print(">> Mode: Dashboard")
        # run_dashboard()
        
    else:
        print(">> No specific mode selected. Running standard mode...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nAborted by user.", "yellow")
    except Exception as e:
        cprint(f"\nCritical Error: {e}","red")
    finally:
        # Keeps window open if double-clicked
        input("\nPress Enter to exit...")

def check_os():
        if platform.system() != "Windows":
            cprint("Critical error: OS not Windows! This software is built for Windows specifically.", "red")
            sys.exit(1)
        else: 
            cprint("Is Windows", "green")