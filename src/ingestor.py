import win32evtlog
import win32evtlogutil
import win32con
import logging

logger = logging.getLogger(__name__)

class EventLogIngestor:
    """
    Handles the ingestion of Windows Event Logs using the Win32 API.
    Prioritizes reading 'Security' logs for forensic analysis.
    """
    def __init__(self, log_type='Security', server='localhost'):
        self.log_type = log_type
        self.server = server

    def fetch_logs(self, event_filter=None, max_events=1000):
        """
        Reads the latest events from the Windows Event Log.
        
        Args:
            event_filter (list): List of Event IDs to filter (e.g., [4625]).
            max_events (int): Safety limit to prevent reading too much data at once.
            
        Returns:
            list: A list of dictionary objects containing raw event data.
        """
        logger.info(f"Starting log ingestion from channel: {self.log_type}")
        logs = []
        
        # Open the event log
        try:
            hand = win32evtlog.OpenEventLog(self.server, self.log_type)
        except Exception as e:
            logger.critical(f"Failed to open Event Log. Do you have Admin privileges? Error: {e}")
            return []

        # Configure flags to read BACKWARDS (newest first)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        total_read = 0

        try:
            while total_read < max_events:
                # Read a batch of events
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if not events:
                    break

                for event in events:
                    # Skip events with no interest
                    if event_filter and event.EventID not in event_filter:
                        continue
                    
                    try:
                        # Normalize the data structure immediately
                        # 'SafeFormatMessage' extracts the full text description
                        msg = win32evtlogutil.SafeFormatMessage(event, self.log_type)
                        
                        data = {
                            "EventID": event.EventID,
                            "TimeGenerated": event.TimeGenerated.isoformat(),
                            "Source": event.SourceName,
                            "Message": msg if msg else "No Message Content"
                        }
                        logs.append(data)
                        total_read += 1
                        
                        if total_read >= max_events:
                            break
                            
                    except Exception as e:
                        logger.error(f"Error parsing specific event {event.EventID}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error during log reading loop: {e}")
        finally:
            win32evtlog.CloseEventLog(hand)
            logger.info(f"Ingestion complete. Read {len(logs)} events.")

        return logs