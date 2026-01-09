import sys
import argparse
import logging
from termcolor import cprint
from colorama import just_fix_windows_console

# Import core modules
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
    parser.add_argument("-d", "--default", action="store_true", help="Run with dashboard")
    parser.add_argument("--stop", action="store_true", help="Stop the background service")
    
    # Terminal Mode Flag
    parser.add_argument("-t", "--terminal", action="store_true", help="Run in Terminal Mode (Text-only Live Monitor)")

    args = parser.parse_args()

    # Handle Modes (Traffic Cop)
    if args.autostart:
        print(">> Mode: Autostart Installation")
        utils.install_scheduled_task()

    elif args.unautostart:
        print(">> Mode: Autostart Removal")
        utils.uninstall_scheduled_task()
        
    elif args.terminal:
        # Run the 'Terminal' mode (Live Monitor in Terminal)
        logging.info("Terminal mode started.")
        core.run_standard_analysis()

    elif args.stop:
        print(">> Mode: Stopping Service")
        logging.info("User trying to stop program.")
        utils.stop_scheduled_task()

    elif args.default:
        print(">> Running in default mode")
        logging.info("Dashboard mode trying to start (Default).")
        
        from src.dashboard import run_dashboard
        run_dashboard()

    else:
        # DEFAULT: Run Dashboard
        print(">> No specific mode selected. Launching Dashboard (Default)...")
        logging.info("Dashboard mode trying to start (Default).")
        
        from src.dashboard import run_dashboard
        run_dashboard()

    logging.info("WinSentry CLI execution finished.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nAborted by user.", "yellow")
    except Exception as e:
        cprint(f"\nCritical Failure: {e}", "red")
        logging.exception("Fatal error in main loop.")