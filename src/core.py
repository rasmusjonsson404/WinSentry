import logging
import pandas as pd
import time
import os
from termcolor import cprint, colored
from src.ingestor import EventLogIngestor
from src.processor import LogProcessor
from src.utils import is_admin

# Get logger
logger = logging.getLogger(__name__)

def clear_screen():
    # Helper to clear terminal window (Windows uses 'cls')
    os.system('cls' if os.name == 'nt' else 'clear')

def run_standard_analysis():
    logger.info("Initializing Live Monitor Mode...")
    
    # --- Check admin privileges immediately ---
    if not is_admin():
        logger.critical("Attempted to run Live Monitor without Admin privileges.")
        print("\n" + colored("CRITICAL ERROR: ACCESS DENIED", "red", attrs=['bold']))
        print(colored("You must run WinSentry as Administrator to access Windows Security Logs.", "red"))
        print("-" * 60)
        print("Windows blocks access to the 'Security' event log for non-admin users.")
        print("Please close this terminal, right-click it, and select 'Run as Administrator'.")
        print("-" * 60)
        input("\nPress Enter to return to menu...") # Pause so the user can read
        return # Abort function
    # --------------------------------------------------

    print("Starting Live Monitor... (Press Ctrl+C to stop)")
    time.sleep(2)

    try:
        while True:
            clear_screen()
            
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print(colored(f"=== WINSENTRY LIVE MONITOR [{current_time}] ===", "cyan", attrs=['bold']))
            print(colored("Scanning Windows Security Logs for Event ID 4625 (Failed Logins)...", "yellow"))
            
            # Fetch Data
            ingestor = EventLogIngestor()
            # We look at the last 100 events to see if any new failures appeared
            raw_logs = ingestor.fetch_logs(event_filter=[4625], max_events=100)
            
            if not raw_logs:
                print("\n" + colored(">> Status: CLEAR", "green"))
                print("No failed login attempts detected in the recent logs.")
            
            else:
                # Process Data
                processor = LogProcessor()
                df = processor.process_logs(raw_logs)
                
                if not df.empty:
                    print("\n" + colored(f">> WARNING: {len(df)} FAILED LOGIN ATTEMPTS DETECTED", "red", attrs=['bold']))
                    print("-" * 60)
                    
                    # Select and rename columns for cleaner output
                    display_cols = ['TimeGenerated', 'Target_User', 'Source_IP', 'Failure_Reason']
                    final_cols = [c for c in display_cols if c in df.columns]
                    
                    # Print the dataframe without the index number
                    print(df[final_cols].to_string(index=False))
                    print("-" * 60)
                else:
                    print("\n" + colored(">> Status: CLEAR (Logs found but filtered out)", "green"))

            print("\nUpdating in 5 seconds... (Ctrl+C to Quit)")
            
            # Wait before next check (Polling)
            time.sleep(5)

    except KeyboardInterrupt:
        # Handles Ctrl+C
        print("\n" + colored(">> Stopping Live Monitor...", "yellow"))
        logger.info("Live Monitor stopped by user.")