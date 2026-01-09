import logging
import logging.config
import logging.handlers
import os
import json
import datetime
import configparser

# --- CUSTOM LOG NAMING LOGIC ---
def log_namer(default_name):
    """
    Reorders the filename during log rotation to keep the .log extension at the end.
    Input from Python:  .../winsentry.log.2026-01-08
    Desired result:     .../winsentry_2026-01-08.log
    """
    # Separate directory path from filename
    dirname, filename = os.path.split(default_name)
    
    # Split filename at dots
    # Example: ['winsentry', 'log', '2026-01-08']
    parts = filename.split('.')
    
    # Check if we have enough parts to swap
    if len(parts) >= 3:
        date_part = parts[-1]       # 2026-01-08
        extension = parts[-2]       # log
        base_name = ".".join(parts[:-2]) # winsentry
        
        # Construct new name: winsentry_2026-01-08.log
        new_filename = f"{base_name}_{date_part}.{extension}"
        return os.path.join(dirname, new_filename)
    
    # If format is unexpected, return original
    return default_name

class CustomRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    A wrapper around TimedRotatingFileHandler to use our custom namer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namer = log_namer
# --- END CUSTOM LOGIC ---

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """
    def format(self, record):
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        
        log_record = {
            "timestamp": utc_time.isoformat(), 
            "level": record.levelname,
            "event_source": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line_number": record.lineno
        }
        
        if hasattr(record, 'error_code'):
            log_record['error_code'] = record.error_code

        if record.exc_info:
            log_record['traceback'] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logging():
    """
    Sets up logging by reading from 'config/settings.conf'.
    If the config file is missing, it creates it with default values 
    for BOTH Logging and Dashboard to keep everything in one place.
    """
    # Find paths (Root directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, "logs")
    
    # Define config directory and file path
    config_dir = os.path.join(base_dir, "config")
    config_file = os.path.join(config_dir, "settings.conf")

    # Ensure directories exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Handle Configuration File (settings.conf)
    config = configparser.ConfigParser()
    
    # Default settings for LOGGING
    logging_defaults = {
        'when': 'midnight',
        'interval': '1',
        'backup_count': '30'
    }
    
    # Default settings for DASHBOARD (We add them here so the file is complete)
    dashboard_defaults = {
        'port': '8050',
        'refresh_interval': '5',
        'max_events': '200'
    }

    if not os.path.exists(config_file):
        # Create file if missing with ALL sections
        config['LOGGING'] = logging_defaults
        config['DASHBOARD'] = dashboard_defaults
        
        try:
            with open(config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            print(f"Warning: Could not create config/settings.conf: {e}")
        
        settings = logging_defaults
    else:
        # Read existing file
        try:
            config.read(config_file)
            if 'LOGGING' in config:
                settings = config['LOGGING']
            else:
                settings = logging_defaults
        except Exception:
            settings = logging_defaults

    # Read values (with error handling)
    log_when = settings.get('when', 'midnight')
    try:
        log_interval = int(settings.get('interval', '1'))
        log_backup = int(settings.get('backup_count', '30'))
    except ValueError:
        log_interval = 1
        log_backup = 30

    # Configure Logger
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
            'rotating_file_handler': {
                # CHANGED: Point to our Custom Class instead of the standard one
                'class': 'src.logger.CustomRotatingFileHandler',
                'filename': log_filename,
                'when': log_when,       
                'interval': log_interval,   
                'backupCount': log_backup, 
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