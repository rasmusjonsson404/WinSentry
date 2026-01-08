# 🏗 System Architecture

## High-Level Overview
WinSentry is designed as a modular pipeline that ingests, processes, and visualizes Windows Event Logs. The system is split into three main layers: **Ingestion**, **Processing**, and **Presentation**, supported by a robust infrastructure for configuration and logging.

## 🔄 Data Flow Diagram
The following diagram illustrates the control flow from the launcher (`Run.bat`) to the various execution modes (Dashboard, Terminal, Service, Test, Maintenance).

```mermaid
graph TD
    A[Start: Run.bat / main.py] --> B{Check Admin Privileges}
    B -- No --> C[Request Elevation / Error]
    B -- Yes --> D[Load Config & Arguments]
    D --> E{Select Mode}

    %% Terminal Mode Path
    E -- "-t / --terminal" --> F[Terminal Monitor]
    F --> F1[Fetch Logs ID 4625]
    F1 --> F2[Print to Console]
    F2 --> F3[Sleep 5s]
    F3 --> F1

    %% Autostart Management Path
    E -- "-a / -u / --stop" --> G[Service Management]
    G --> G1{Action?}
    G1 -- Add --> G2[Task Scheduler: Create Task]
    G1 -- Remove --> G3[Task Scheduler: Delete Task]
    G1 -- Stop --> G4[Task Scheduler: End Task]

    %% Test & Maintenance Paths
    E -- "Run Test" --> T[Test Script: Generate Events]
    T --> T1[Simulate Failed Logins]
    T1 -.-> M

    E -- "Reset Logs" --> R[Reset Script: Clear Logs]
    R --> R1[System Command: wevtutil cl Security]
    R1 -.-> M

    %% Dashboard Mode (Default) Path
    E -- Default --> H[Dashboard Server]
    H --> I[Initialize Dash App]
    I --> J[Start Web Server :8050]
    J --> K[Open Browser]
    
    subgraph "Background Loop (Interval)"
        L[Timer Trigger] --> M[Ingestor: Fetch Logs]
        M --> N[Processor: Normalize Data]
        N --> O[Pandas DataFrame]
        O --> P[Update Graphs & KPIs]
    end

    J -.-> L