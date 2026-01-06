import logging
import logging.config
import logging.handlers # Viktig import för rotation
import os
import json
import datetime

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    Fulfills the requirement for structured logging.
    """
    def format(self, record):
        # Use timezone-aware UTC
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Create a dictionary structure for the log entry
        log_record = {
            "timestamp": utc_time.isoformat(), 
            "level": record.levelname,
            "event_source": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line_number": record.lineno
        }
        
        # If there is an error code passed in 'extra' arguments, add it
        if hasattr(record, 'error_code'):
            log_record['error_code'] = record.error_code

        # If there is an exception/crash, add the traceback
        if record.exc_info:
            log_record['traceback'] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logging():
    """
    Sets up the logging configuration with Log Rotation.
    
    - Writes to 'logs/winsentry.log'.
    - Rotates the log file every midnight.
    - Keeps the last 30 days of logs (Retention Policy).
    """
    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Using a static filename for the active logging.
    # Automatically rename old files with date.
    log_filename = os.path.join(log_dir, "winsentry.log")

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
        },
        'handlers': {
            # TimedRotatingFileHandler
            'rotating_file_handler': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': log_filename,
                'when': 'midnight',      # Rotate at midnight
                'interval': 1,           # Every day (once per midnight)
                'backupCount': 30,       # Save the latest 30 files (erase older ones)
                'formatter': 'json',
                'encoding': 'utf-8',
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['rotating_file_handler'],
            'level': 'DEBUG',
        },
    }

    logging.config.dictConfig(logging_config)
    
    return log_filename