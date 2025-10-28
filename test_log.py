#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from log_utils import send_log
import time

def test_logging():
    """Simple test of the logging system"""
    print("Testing logging system...")

    send_log("Test message 1")
    time.sleep(1)

    send_log("Test message 2")
    time.sleep(1)

    send_log("Processing completed!")

    print("Done! Check your browser to see the messages in the log panel.")

if __name__ == "__main__":
    test_logging()
