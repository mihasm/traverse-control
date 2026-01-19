#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic usage example for Serial Koordinatka

This script demonstrates basic motor control operations with the ISEL IMC-S8 controller.
"""

import sys
import time
from commands import Traverse

def main():
    # Initialize the traverse system
    # Adjust the port according to your system:
    # - Windows: 'COM1', 'COM2', etc.
    # - Linux: '/dev/ttyUSB0', '/dev/ttyACM0', etc.
    port = 'COM9'  # Change this to match your setup

    try:
        print(f"Connecting to ISEL IMC-S8 on port {port}...")
        traverse = Traverse(port=port)

        print("Initializing controller for 3-axis operation...")
        traverse.initialize(num_axes=3)

        print("Getting version information...")
        traverse.get_version_data()

        print("Performing reference run (returning to origin)...")
        traverse.reference_run()

        print("Moving to position (100mm, 100mm, 100mm)...")
        traverse.execute_absolute_movement(100, 100, 100)

        print("Getting current position...")
        traverse.get_position()

        print("Moving to position (500mm, 200mm, 300mm)...")
        traverse.execute_absolute_movement(500, 200, 300)

        print("Getting final position...")
        traverse.get_position()

        print("Demo completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the controller is connected and powered on.")
        sys.exit(1)

if __name__ == "__main__":
    main()