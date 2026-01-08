# WinSentry Documentation

## 1. System Overview
**WinSentry** is a cybersecurity monitoring tool designed to ingest, normalize, and visualize Windows Security Event Logs in real-time. It acts as a lightweight Intrusion Detection System (IDS), specifically monitoring **Event ID 4625** (Failed Logon Attempts) to detect brute-force attacks and unauthorized access.

The application is built with a **defensive architecture**, incorporating strict environment checks for operating system compatibility and administrator privileges to ensure stability.

### Core Capabilities
* **Live Data Ingestion:** Utilizes the Win32 API to read raw Windows Event Logs immediately as they occur.
* **Forensic Normalization:** Parses unstructured log messages using Regular Expressions (Regex) to extract critical data points like IP addresses and user accounts.
* **Dual-Mode Interface:** Provides both a command-line text monitor and a graphical web dashboard.
* **Persistent Monitoring:** Includes an autostart capability to run silently as a background service upon system boot.

---

## 2. Installation & Setup

### Prerequisites
* **Operating System:** Windows 10 or Windows 11.
* **Python:** Version 3.9 or higher.
* **Privileges:** **Administrator rights are mandatory** to access the Windows Security Log.

### Setup Steps
1.  **Clone the Repository:** Download the project files to a local directory.
2.  **Execute Setup Script:** Run `Setup.bat`. This script automates the initialization process by:
    * Detecting the installed Python version.
    * Creating a virtual environment (`.venv`) to isolate dependencies.
    * Installing required libraries (e.g., `pywin32`, `dash`, `pandas`) from `requirements.txt`.

---

## 3. Usage Guide

### Running the Application
The primary entry point is **`Run.bat`**. This wrapper script automatically requests Administrator privileges and activates the virtual environment before launching the main program.

#### Main Menu Options
Upon running `Run.bat`, you are presented with the following options:
1.  **Run WinSentry (Dashboard Mode):** Starts the web server for graphical monitoring.
2.  **Run WinSentry (Terminal Mode):** Starts the text-based live monitor.
3.  **Show help page:** Displays command-line arguments.
4.  **Run with your own arguments:** Allows manual input of CLI flags.
5.  **Add to Windows startup:** Configures the tool to run hidden at boot.
6.  **Remove from Windows startup:** Disables the autostart task.
7.  **Stop background service:** Kills any running background instances.

### Command Line Interface (CLI)
Advanced users can run `main.py` directly using the virtual environment's Python executable.
**Available Arguments**:
* `-t`, `--terminal`: Launch Terminal Mode (Text-only monitor).
* `-a`, `--autostart`: Install the scheduled task for system startup.
* `-u`, `--unautostart`: Remove the scheduled task.
* `--stop`: Forcefully stop the background service.
* `-v`, `--version`: Display version information.

---

## 4. Operation Modes

### Dashboard Mode (Web Interface)
* **Default Port:** `8050` (Configurable).
* **Features**:
    * **KPI Cards:** Real-time counters for Total Failures and Top Attacker IP.
    * **Attack Timeline:** A dynamic line graph showing attack frequency.
    * **Failure Reasons:** A pie chart visualizing error types (e.g., "Bad Password").
    * **Live Event Table:** A detailed list of the most recent failed login attempts.
    * **System Diagnostics:** A view of the internal `winsentry.log` file.

### Terminal Mode (Text Monitor)
* **Function:** Clears the console and polls the Security Log every 5 seconds.
* **Output:** Displays a "Safe" status when idle. Upon detecting a failed login (Event 4625), it alerts the user with a red warning and prints a table containing the Time, Target User, Source IP, and Failure Reason.

---

## 5. Configuration
Configuration is managed via `config/settings.conf`. If missing, the system generates a default file on the first run.

### `[LOGGING]` Section
Controls the internal application logs stored in the `/logs` directory.
* `when`: Log rotation timing (default: `midnight`).
* `interval`: Rotation frequency (default: `1`).
* `backup_count`: Number of historical log files to retain (default: `30`).

### `[DASHBOARD]` Section
Controls the web server behavior.
* `port`: HTTP port for the dashboard (default: `8050`).
* `refresh_interval`: Dashboard data update rate in seconds (default: `5`).
* `max_events`: Maximum number of recent events to process for visualization (default: `200`).

---

## 6. Technical Architecture

### Data Ingestion
The `EventLogIngestor` class (`src/ingestor.py`) interfaces with the Windows Event Log via `win32evtlog`. It reads the **Security** channel in reverse order (newest first) to ensure low latency and specifically filters for Event ID **4625**.

### Data Processing
The `LogProcessor` class (`src/processor.py`) normalizes raw log data into a structured Pandas DataFrame. It uses Regex to parse the message field:
* **IP Extraction:** `Source Network Address:\s*([0-9]{...})`
* **User Extraction:** `Account Name:\s*(\w+)`
* **Status Mapping:** Converts Hex codes (e.g., `0xc000006a`) into human-readable reasons (e.g., "Wrong Password").

### Autostart Mechanism
Persistence is achieved using the **Windows Task Scheduler** (`schtasks`).
* **Task Name:** "WinSentry".
* **Trigger:** System Startup (`ONSTART`).
* **Privilege Level:** `HIGHEST` (Admin).

### Logging System
Internal logs are serialized in JSON format to facilitate machine parsing and integration with external SIEM tools.
* **Format:** `{"timestamp": "...", "level": "...", "message": "..."}`.

---

## 7. Troubleshooting

* **Error: "Access Denied" or "Failed to open Event Log"**
    * **Cause:** The application is running without Administrator privileges.
    * **Solution:** Use `Run.bat` or right-click your terminal and select "Run as Administrator".

* **Error: "Log file not found" in Dashboard**
    * **Cause:** The application has not yet generated a log file or the `logs/` directory is missing.
    * **Solution:** Run the application once to initialize the logging directory and file.

* **Background Service Not Stopping**
    * **Cause:** The task "WinSentry" is not currently running in the Task Scheduler.
    * **Solution:** Use the menu option "Stop background service" to ensure the task is terminated correctly using `schtasks /End`.