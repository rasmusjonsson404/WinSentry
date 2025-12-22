import sys
import platform
import argparse
from termcolor import colored, cprint
from src import utils

def main():

    parser = argparse.ArgumentParser(
        description="WinSentry: Windows Security Log Analyzer & Visualizer",
        epilog="Developed for Applied Scripting Course."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="WinSentry v0.0.3",
        help="Show program version and exit."
    )

    parser.add_argument(
        "--install",
        action="store_true",
        help="Install WinSentry to Windows Task Scheduler (Requires Admin)."
    )

    # This line reads sys.argv and matches it against rules above.
    # If -h is used, it prints help and exits here.
    args = parser.parse_args()

    # --- STEP 4: Use the values ---
    print("--- WinSentry Initialized ---")

    if args.install:
        print(">> Mode: Installation")
        # install_autostart()
        
    elif args.dashboard:
        print(">> Mode: Dashboard")
        # run_dashboard()
        
    elif args.file:
        print(f">> Mode: Offline Analysis of file: {args.file}")
        # analyze_file(args.file)
        
    else:
        print(">> No specific mode selected. Running default scan...")
        # default_scan()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
    except Exception as e:
        print(f"\nCritical Error: {e}")
    finally:
        # Keeps window open if double-clicked
        input("\nPress Enter to exit...")

def arg_handler():
     
     parser = argparse.ArgumentParser(
        description="WinSentry: Windows Security Log Analyzer & Visualizer",
        epilog="Developed for Applied Scripting Course."
    )

def check_os():
        if platform.system() != "Windows":
            cprint("Critical error: OS not Windows! This software is built for Windows specifically.", "red")
            sys.exit(1)
        else: 
            cprint("Is Windows", "green")