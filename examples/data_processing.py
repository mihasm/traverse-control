#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data processing example for Serial Koordinatka

This script demonstrates how to process measurement data and generate visualizations.
Run this after completing automated measurements.
"""

import sys
import os
import glob
import procesiranje

def main():
    # Find the most recent measurement directory
    measurement_dirs = glob.glob('meritve/meritve_*')
    if not measurement_dirs:
        print("No measurement directories found in 'meritve/'")
        print("Make sure you have completed automated measurements first.")
        sys.exit(1)

    # Use the most recent measurement directory
    measurement_dir = max(measurement_dirs, key=os.path.getctime)
    print(f"Processing data from: {measurement_dir}")

    try:
        # Find traverse location files
        casi_files = glob.glob(os.path.join(measurement_dir, 'casi_*'))
        if not casi_files:
            print("No traverse location files found!")
            sys.exit(1)

        print(f"Found {len(casi_files)} measurement file(s)")

        # Process each measurement file
        for casi_file in casi_files:
            print(f"\nProcessing: {os.path.basename(casi_file)}")

            # Correlate traverse positions with measurement data
            correlated_data = procesiranje.correlate_data(casi_file, measurement_dir)
            print(f"Correlated {len(correlated_data)} measurement points")

            # Generate visualization plots
            print("Generating plots...")
            procesiranje.izrisi_tocke(correlated_data, casi_file, measurement_dir)

        print("\nData processing completed!")
        print("Check the 'slikice' and 'slikice_absolute' directories for plots.")
        print("Combined results are available in 'results/' directory.")

    except Exception as e:
        print(f"Error during data processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()