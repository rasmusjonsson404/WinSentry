import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging
import os
import threading
import msvcrt
import time
import webbrowser
import configparser
from termcolor import colored
from datetime import datetime
from collections import deque

# Import our own modules
from src.ingestor import EventLogIngestor
from src.processor import LogProcessor
from src.utils import is_admin
from src.logger import setup_logging

# Configure logs
logger = logging.getLogger(__name__)

# --- STYLING (Dark Theme) ---
COLORS = {
    'background': '#0e1012',
    'paper': '#161b22',
    'text': '#c9d1d9',
    'accent': '#58a6ff',
    'danger': '#f85149',
    'success': '#3fb950',
    'warning': '#d29922',
    'border': '#000000'
}

def load_settings():
    """
    Reads settings from config/settings.conf.
    Returns a dictionary with configuration values.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(base_dir, "config", "settings.conf")
    
    config = configparser.ConfigParser()
    
    # Default values if file or keys are missing
    defaults = {
        'port': 8050,
        'refresh_interval': 5,
        'max_events': 200
    }
    
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            if 'DASHBOARD' in config:
                section = config['DASHBOARD']
                return {
                    'port': section.getint('port', 8050),
                    'refresh_interval': section.getint('refresh_interval', 5),
                    'max_events': section.getint('max_events', 200)
                }
        except Exception as e:
            logger.error(f"Error reading settings.conf: {e}")
            
    return defaults

def get_program_logs(num_lines=20):
    """Reads the last N lines from the active log file."""
    log_dir = "logs"
    try:
        # Find the latest log file (winsentry.log)
        log_file = os.path.join(log_dir, "winsentry.log")
        
        if not os.path.exists(log_file):
            return ["Log file not found."]

        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-num_lines:]
    except Exception as e:
        return [f"Error reading logs: {e}"]

def wait_for_shutdown_key():
    """Listens for Ctrl+Q in the terminal and force quits the program."""
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x11':
                print(colored("\n\n>> [User Request] Ctrl+Q detected. Shutting down WinSentry...", "yellow"))
                logger.info("User requested shutdown via Ctrl+Q.")
                os._exit(0)
        time.sleep(0.1)

def run_dashboard():
    """Starts the Dash web server."""
    
    if not is_admin():
        print("CRITICAL: Dashboard requires Admin privileges to read Security Logs.")
        return

    logger.info("Initializing Dash Dashboard...")

    # Load Settings
    settings = load_settings()
    PORT = settings['port']
    REFRESH_INTERVAL_SEC = settings['refresh_interval']
    MAX_EVENTS = settings['max_events']
    
    logger.info(f"Configuration loaded: Port={PORT}, Refresh={REFRESH_INTERVAL_SEC}s")

    app = dash.Dash(__name__, title="WinSentry Dashboard")
    
    # Define Layout
    app.layout = html.Div(style={
        'backgroundColor': COLORS['background'], 
        'minHeight': '100vh', 
        'padding': '20px', 
        'fontFamily': 'Segoe UI, sans-serif', 
        'color': COLORS['text'],
        'border': f'10px solid {COLORS["border"]}',
        'boxSizing': 'border-box'
    }, children=[
        
        # --- HEADER ---
        html.Div([
            html.H1("WinSentry Live Monitor", style={'color': COLORS['accent'], 'display': 'inline-block'}),
            html.Div(id='live-clock', style={'float': 'right', 'fontSize': '20px', 'marginTop': '10px', 'fontFamily': 'monospace'})
        ], style={'borderBottom': f'1px solid {COLORS["border"]}', 'marginBottom': '20px'}),

        # --- KPI CARDS ---
        html.Div([
            html.Div([
                html.H3("Total Failures", style={'margin': '0'}),
                html.H1(id='kpi-total', children="0", style={'color': COLORS['danger'], 'margin': '0'})
            ], style={'backgroundColor': COLORS['paper'], 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'textAlign': 'center', 'border': f'1px solid {COLORS["border"]}'}),
            
            html.Div([
                html.H3("Top Attacker IP", style={'margin': '0'}),
                html.H2(id='kpi-top-ip', children="N/A", style={'color': COLORS['accent'], 'margin': '10px 0'})
            ], style={'backgroundColor': COLORS['paper'], 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'textAlign': 'center', 'border': f'1px solid {COLORS["border"]}'}),

            html.Div([
                html.H3("Last Heartbeat", style={'margin': '0'}),
                html.H2(id='kpi-status', children="Initializing...", style={'color': COLORS['success'], 'margin': '10px 0'})
            ], style={'backgroundColor': COLORS['paper'], 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'textAlign': 'center', 'border': f'1px solid {COLORS["border"]}'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

        # --- GRAPHS ---
        html.Div([
            # Graph 1: Timeline (With Dropdown)
            html.Div([
                html.Div([
                    html.Span("Resolution: ", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='time-granularity-selector',
                        options=[
                            {'label': 'Seconds', 'value': 's'},
                            {'label': 'Minutes', 'value': 'min'},
                            {'label': 'Hours', 'value': 'h'},
                            {'label': 'Days', 'value': 'd'}
                        ],
                        value='min',
                        clearable=False,
                        style={'color': '#000', 'width': '150px', 'display': 'inline-block', 'verticalAlign': 'middle'}
                    )
                ], style={'marginBottom': '10px', 'textAlign': 'right'}),
                
                dcc.Graph(id='graph-timeline', style={'height': '350px'})
            ], style={'width': '65%', 'backgroundColor': COLORS['paper'], 'padding': '10px', 'borderRadius': '10px', 'border': f'1px solid {COLORS["border"]}'}),

            # Graph 2: Reasons
            html.Div([
                dcc.Graph(id='graph-reasons', style={'height': '350px'})
            ], style={'width': '33%', 'backgroundColor': COLORS['paper'], 'padding': '10px', 'borderRadius': '10px', 'border': f'1px solid {COLORS["border"]}'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

        # --- DATA & LOGS ---
        html.Div([
            html.Div([
                html.H4("Recent Security Events (ID 4625)", style={'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div(id='table-container')
            ], style={'width': '58%', 'backgroundColor': COLORS['paper'], 'padding': '20px', 'borderRadius': '10px', 'border': f'1px solid {COLORS["border"]}'}),

            html.Div([
                html.H4("Program Diagnostics (winsentry.log)", style={'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Pre(id='program-logs', style={
                    'backgroundColor': '#0d1117', 
                    'color': '#8b949e', 
                    'padding': '10px', 
                    'height': '300px', 
                    'overflowY': 'scroll',
                    'fontSize': '12px',
                    'border': f'1px solid {COLORS["border"]}'
                })
            ], style={'width': '38%', 'backgroundColor': COLORS['paper'], 'padding': '20px', 'borderRadius': '10px', 'border': f'1px solid {COLORS["border"]}'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        dcc.Interval(
            id='interval-component',
            interval=REFRESH_INTERVAL_SEC * 1000, 
            n_intervals=0
        )
    ])

    @app.callback(
        [Output('kpi-total', 'children'),
         Output('kpi-top-ip', 'children'),
         Output('graph-timeline', 'figure'),
         Output('graph-reasons', 'figure'),
         Output('table-container', 'children'),
         Output('program-logs', 'children'),
         Output('live-clock', 'children'),
         Output('kpi-status', 'children')],
        [Input('interval-component', 'n_intervals'),
         Input('time-granularity-selector', 'value')]
    )
    def update_metrics(n, granularity_code):
        current_settings = load_settings()
        limit_events = current_settings['max_events']

        now_str = datetime.now().strftime("%H:%M:%S")
        status_msg = f"ACTIVE ({now_str})"
        
        ingestor = EventLogIngestor()
        raw_logs = ingestor.fetch_logs(event_filter=[4625], max_events=limit_events)
        
        processor = LogProcessor()
        df = processor.process_logs(raw_logs)

        log_lines = get_program_logs()
        log_text = "".join(log_lines)

        if df.empty:
            empty_fig = px.line(title="No Data Available").update_layout(
                plot_bgcolor=COLORS['paper'], paper_bgcolor=COLORS['paper'], font_color=COLORS['text']
            )
            return "0", "N/A", empty_fig, empty_fig, "No failed logins detected recently.", log_text, now_str, status_msg

        # Ensure forensic columns exist (prevents KeyErrors if regex fails)
        for col in ['Source_IP', 'Target_User', 'Failure_Reason']:
            if col not in df.columns:
                df[col] = "N/A"

        total_failures = len(df)
        top_ip = df['Source_IP'].mode()[0] if not df['Source_IP'].mode().empty else "N/A"

        # Dynamic grouping based on drop-down
        # 's' = Second, 'min' = Minute, 'h' = Hour, 'd' = Day
        df['Time'] = pd.to_datetime(df['TimeGenerated']).dt.floor(granularity_code)
        
        df_time = df.groupby('Time').size().reset_index(name='Count')
        
        # Update title
        titles = {'s': 'Attack Timeline (Per Second)', 'min': 'Attack Timeline (Per Minute)', 'h': 'Attack Timeline (Per Hour)', 'd': 'Attack Timeline (Per Day)'}
        chart_title = titles.get(granularity_code, 'Attack Timeline')

        fig_timeline = px.line(df_time, x='Time', y='Count', title=chart_title, markers=True)
        fig_timeline.update_layout(
            plot_bgcolor=COLORS['paper'], paper_bgcolor=COLORS['paper'], font_color=COLORS['text'],
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=COLORS['border'])
        )

        df_reasons = df['Failure_Reason'].value_counts().reset_index()
        df_reasons.columns = ['Reason', 'Count']
        fig_reasons = px.pie(df_reasons, values='Count', names='Reason', title='Failure Reasons', hole=0.4)
        fig_reasons.update_layout(
            plot_bgcolor=COLORS['paper'], paper_bgcolor=COLORS['paper'], font_color=COLORS['text']
        )

        display_cols = ['TimeGenerated', 'Target_User', 'Source_IP', 'Failure_Reason']
        valid_cols = [c for c in display_cols if c in df.columns]
        
        table_data = df[valid_cols].head(10).astype(str).to_dict('records')
        
        table = dash_table.DataTable(
            data=table_data,
            columns=[{'name': i, 'id': i} for i in valid_cols],
            style_header={'backgroundColor': '#21262d', 'color': COLORS['text'], 'fontWeight': 'bold', 'border': f'1px solid {COLORS["border"]}'},
            style_cell={'backgroundColor': COLORS['background'], 'color': COLORS['text'], 'border': f'1px solid {COLORS["border"]}'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'background_color': COLORS['paper']}
            ]
        )

        return str(total_failures), top_ip, fig_timeline, fig_reasons, table, log_text, f"Server Time: {now_str}", status_msg

    print("\n" + "="*50)
    print("  WINSENTRY DASHBOARD SERVER")
    print("="*50)
    
    link = colored(f"http://127.0.0.1:{PORT}/", "cyan", attrs=["underline"])
    print(f">> Server running at: {link}")
    print(">> Opening browser automatically...")
    print(">> Press Ctrl+Q to shut down the server and exit.")
    print("="*50 + "\n")

    monitor_thread = threading.Thread(target=wait_for_shutdown_key, daemon=True)
    monitor_thread.start()

    webbrowser.open(f"http://127.0.0.1:{PORT}/")

    app.run(debug=False, port=PORT)