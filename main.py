import sys
import platform
import argparse
import logging
from termcolor import colored, cprint
from src import utils
from src.logger import setup_logging
from colorama import just_fix_windows_console

just_fix_windows_console()

def main():
    # Setup logging immediately
    log_file = setup_logging()
    logging.info("WinSentry initialized.")

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

    # Log that we are parsing arguments
    logging.debug("Parsing command line arguments.")
    args = parser.parse_args()

    if args.autostart:
        print(">> Mode: Installation of autostart")
        logging.info("User selected mode: Autostart Installation")
        utils.install_scheduled_task()

    elif args.unautostart:
        print(">> Mode: Uninstallation of autostart")
        logging.info("User selected mode: Autostart Uninstallation")
        utils.uninstall_scheduled_task()
        
    elif args.dashboard:
        print(">> Mode: Dashboard")
        logging.info("User selected mode: Dashboard")
        # run_dashboard()
        
    else:
        print(">> No specific mode selected. Running standard mode...")
        logging.info("Running standard mode.")

    logging.info("WinSentry finished successfully.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nAborted by user.", "yellow")
        logging.warning("Execution aborted by user (KeyboardInterrupt).")
    except Exception as e:
        cprint(f"\nCritical Error: {e}","red")
        # logging.exception saves "Traceback"
        logging.exception("Critical error occurred during execution.")
    finally:
        # Keeps window open if double-clicked
        input("\nPress Enter to exit...")