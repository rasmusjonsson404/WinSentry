import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

class LogProcessor:
    """
    Processes raw event logs into structured DataFrames.
    Implements forensic logic (Regex) to extract IP addresses and Usernames.
    """
    def __init__(self):
        # Regex patterns defined in requirements [cite: 120-122]
        self.patterns = {
            # Extracts IP Address (Source Network Address)
            'ip_address': r"Source Network Address:\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
            
            # Extracts User Account (Account Name)
            'account_name': r"Account Name:\s*(\w+)",
            
            # Extracts Failure Status Code (Hex)
            'status_code': r"Failure Status:\s*(0x[0-9a-fA-F]+)"
        }
        
        # Mapping hex codes to human readable reasons [cite: 126-128]
        self.status_mapping = {
            "0xc0000064": "Non-existent User (Enumeration)",
            "0xc000006a": "Wrong Password (Brute-Force)",
            "0xc000006d": "Bad Username or Password"
        }

    def process_logs(self, raw_logs):
        """
        Converts raw log dictionaries to a cleaned Pandas DataFrame.
        """
        if not raw_logs:
            logger.warning("No logs to process.")
            return pd.DataFrame()

        logger.debug(f"Processing {len(raw_logs)} raw log entries...")
        
        # Create initial DataFrame
        df = pd.DataFrame(raw_logs)

	# Set EventID to 0 if missing. Prevents script from crashing.
        if 'EventID' not in df.columns:
            df['EventID'] = 0        
        
	# Apply Regex Extraction for Event ID 4625 (Failed Login)
        # We only apply this logic to rows where EventID is 4625
        mask_4625 = df['EventID'] == 4625
        
        if mask_4625.any():
            logger.info("Extracting forensic data from 4625 events...")
            
            # Extract IP
            df.loc[mask_4625, 'Source_IP'] = df.loc[mask_4625, 'Message'].str.extract(
                self.patterns['ip_address'], expand=False
            )
            
            # Extract Account
            # Note: 4625 often contains the machine account first
            df.loc[mask_4625, 'Target_User'] = df.loc[mask_4625, 'Message'].str.extract(
                self.patterns['account_name'], expand=False
            )
            
            # Extract Status Code
            df.loc[mask_4625, 'Status_Hex'] = df.loc[mask_4625, 'Message'].str.extract(
                self.patterns['status_code'], expand=False
            ).str.lower() # Normalize to lowercase for mapping
            
            # Map Hex codes to Human Readable Text
            df.loc[mask_4625, 'Failure_Reason'] = df.loc[mask_4625, 'Status_Hex'].map(
                self.status_mapping
            ).fillna("Unknown Error")
            
        else:
            logger.info("No Event ID 4625 found in this batch.")

        # Fill NaNs for cleaner display
        df.fillna("N/A", inplace=True)
        
        return df
