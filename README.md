<div align="center">
  <img src="assets/display/WinSentry_log_txt.png" alt="WinSentry Logo" width="1000">
  <p>
    <b>Windows Security Log Analyzer</b>
  </p>
  <br>
</div>

**WinSentry** is a robust, automated cybersecurity tool designed to ingest, normalize, and visualize Windows Event Logs in real-time. Developed as part of the "Applied Scripting" course, this application transforms unstructured security data (specifically Event ID 4625) into actionable intelligence via an interactive web dashboard.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)

## 🔭 Project Overview
The primary mission of WinSentry is to detect potential security threats, such as brute-force attacks, by monitoring the Windows Security Log. Unlike simple scripts, WinSentry utilizes a **defensive programming architecture** to ensure resilience against crashes and environment errors.

It reads raw Windows Event Logs via the Win32 API, parses complex message strings using Regular Expressions (Regex), and visualizes the data using **Dash** and **Pandas**.

## ✨ Key Features
* **Live Data Ingestion:** Real-time reading of Windows Event Logs using `pywin32`.
* **Forensic Normalization:** Extracts critical data (IP Address, User Account, Failure Status) from unstructured text using advanced Regex.
* **Interactive Dashboard:** A web-based UI built with Dash/Plotly displaying security KPIs and attack timelines.
* **Robust Architecture:** Implements strict environment checks (OS & Admin privileges) and "crash-safe" error handling.
* **Structured Logging:** All internal application events are logged in JSON format for full traceability.

## 💻 System Requirements
Due to reliance on the Windows API (`win32evtlog`), this application has strict platform requirements:

* **OS:** Windows 10 or Windows 11.
* **Python:** Version 3.9 or higher.
* **Privileges:** **Administrator rights are mandatory**.
    * *Reason:* Accessing the Windows `Security` event log requires elevated privileges. The script will perform a self-check and exit if these rights are missing.

## ⚙️ Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/rasmusjonsson404/WinSentry.git](https://github.com/rasmusjonsson404/WinSentry.git)
    cd WinSentry
    ```

2.  **Create a Virtual Environment** \
    Run the `Setup.bat` to create a .venv and intall the required libraries for python.

## 🚀 Usage

WinSentry is controlled via a Command Line Interface (CLI). **Note:** You must run your terminal as Administrator.

### Start the Dashboard
To start the full system (Ingestion + Web Server):
```bash
python main.py --mode dashboard