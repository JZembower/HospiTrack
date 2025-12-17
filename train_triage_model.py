#!/usr/bin/env python3
"""
Script to train the ML triage model.

Usage:
    python train_triage_model.py [path_to_data.csv]

If no path is provided, uses /home/ubuntu/Uploads/data.csv by default.
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.triage_ml import train_triage_model


def main():
    # Default data path
    data_path = "/home/ubuntu/Uploads/data.csv"
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    
    if not os.path.exists(data_path):
        print(f"ERROR: Data file not found: {data_path}")
        print("Please provide a valid path to the triage CSV file.")
        return 1
    
    print("=" * 70)
    print("HospiTrack ML Triage Model Training")
    print("=" * 70)
    print(f"Data source: {data_path}")
    print()
    print("⚠️  IMPORTANT: This model is for DEMONSTRATION purposes only.")
    print("    NOT validated for clinical use.")
    print()
    
    try:
        model = train_triage_model(data_path, save_model=True)
        print()
        print("=" * 70)
        print("✓ Training complete!")
        print("=" * 70)
        print(f"Model saved to: models/triage_model.pkl")
        print(f"Encoders saved to: models/triage_encoders.pkl")
        print()
        print("You can now use the ML triage model via the /api/triage endpoint")
        print("with use_ml_model=true in the request body.")
        print()
        return 0
    
    except Exception as e:
        print()
        print("=" * 70)
        print("✗ Training failed!")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
