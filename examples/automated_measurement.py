#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated measurement example for Serial Koordinatka

This script demonstrates automated plane traversal for wind tunnel measurements.
Make sure your anemometer is configured to log data to XLS files.
"""

import sys
import os
from commands import Traverse

def main():
    # Configuration
    port = 'COM9'  # Change this to match your setup
    measurement_plane = "zy"  # Plane to traverse (zy, xz, xy, etc.)
    start_coords = (0, 0)     # Starting coordinates in the plane
    end_coords = (1000, 1000) # Ending coordinates in the plane
    steps = (5, 5)           # Number of steps in each direction
    delay = 10               # Delay at each measurement point (seconds)

    try:
        print(f"Connecting to ISEL IMC-S8 on port {port}...")
        traverse = Traverse(port=port)

        print("Initializing controller for 3-axis operation...")
        traverse.initialize(num_axes=3)

        print("Performing reference run...")
        traverse.reference_run()

        print("Starting automated measurement traversal...")
        print(f"Plane: {measurement_plane}")
        print(f"Start: {start_coords}mm, End: {end_coords}mm")
        print(f"Steps: {steps}, Delay: {delay}s")
        print("Make sure your anemometer is logging data!")

        # This will traverse the plane and create measurement files
        traverse.traverse_plane(
            x1=start_coords[0], y1=start_coords[1],
            x2=end_coords[0], y2=end_coords[1],
            st_x=steps[0], st_y=steps[1],
            delay=delay,
            plane=measurement_plane
        )

        # Note: The traverse_plane method will play a sound when finished
        # and create data files in the 'meritve_' directory

    except KeyboardInterrupt:
        print("\nMeasurement interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the controller is connected and powered on.")
        sys.exit(1)

if __name__ == "__main__":
    main()