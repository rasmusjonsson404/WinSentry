import sys
import argparse
import logging
from termcolor import cprint
from colorama import just_fix_windows_console
from src import utils, core 
from src.logger import setup_logging

just_fix_windows_console()

def main():
    # Setup Logging
    setup_logging()
    logging.info("WinSentry CLI started.")

    # Setup Arguments
    parser = argparse.ArgumentParser(
        description="WinSentry: Windows Security Log Analyzer & Visualizer",
    )
    
    parser.add_argument("-v", "--version", action="version", version="WinSentry v0.1.0")
    parser.add_argument("-a", "--autostart", action="store_true", help="Install Autostart Task")
    parser.add_argument("-u", "--unautostart", action="store_true", help="Remove Autostart Task")
    parser.add_argument("-d", "--dashboard", action="store_true", help="Launch Web Dashboard")
    parser.add_argument("-s", "--standard", action="store_true", help="Run Standard Security Scan")

    args = parser.parse_args()

    # Run correct mode
    if args.autostart:
        print(">> Mode: Autostart Installation")
        logging.info("Trying to add program to windows startup.")
        utils.install_scheduled_task()

    elif args.unautostart:
        print(">> Mode: Autostart Removal")
        logging.info("Trying to remove program to windows startup.")
        utils.uninstall_scheduled_task()
        
    elif args.dashboard:
        print(">> Mode: Dashboard Launch")
        logging.info("Dashboard mode started.")
        # from src.dashboard import run_dashboard
        # run_dashboard()
        
    elif args.standard:
        # Run standard mode
        logging.info("Standard mode started.")
        core.run_standard_analysis()
        
    else:
        # Standard if no arg was passed
        print(">> No specific mode selected. Running default scan...")
        logging.info("Standard mode started.")
        core.run_standard_analysis()

    logging.info("WinSentry CLI execution finished.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nAborted by user.", "yellow")
        logging.info("Program aborted by user.")
    except Exception as e:
        cprint(f"\nCritical Failure: {e}", "red")
        logging.exception("Fatal error in main loop.")