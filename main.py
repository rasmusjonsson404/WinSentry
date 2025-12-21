import sys
import platform
import argparse
from termcolor import colored, cprint

def arg_handler():
     
     parser = argparse.ArgumentParser(
        description="WinSentry: Windows Security Log Analyzer & Visualizer",
        epilog="Developed for Applied Scripting Course."
    )

def check_os():
        if platform.system() != "Windows":
            cprint("Critical error: OS not Windows! This software is built for Windows specifically.", "red")
            sys.exit(1)
        else: 
            cprint("Is Windows", "green")