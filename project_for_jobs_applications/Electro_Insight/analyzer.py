import pandas as pd
import numpy as np
from scipy.signal import find_peaks, savgol_filter

def process_cv_file(filepath):
    """
    Reads a raw CV CSV and calculates electrochemical metrics.
    """
    # Load Data
    df = pd.read_csv(filepath)
    
    # 1. Signal Smoothing (Savitzky-Golay filter)
    # This removes the "instrument noise"
    df['Smooth_Current'] = savgol_filter(df['Current_uA'], window_length=21, polyorder=2)
    
    # 2. Find Anodic Peak (Oxidation)
    # We look for local maxima
    peaks, _ = find_peaks(df['Smooth_Current'], height=2)
    
    if len(peaks) > 0:
        # Take the highest peak found
        best_peak_idx = peaks[np.argmax(df['Smooth_Current'].iloc[peaks])]
        epa = df['Potential_V'].iloc[best_peak_idx] # Peak Potential
        ipa = df['Smooth_Current'].iloc[best_peak_idx] # Peak Current
    else:
        epa, ipa = 0, 0 # Fallback if no peak found
        
    # 3. Quality Check Logic (Business Logic for MSD)
    # If peak current is low, the material isn't conductive enough
    qc_status = "PASS" if ipa > 9.0 else "FAIL"
    
    return {
        "filename": filepath,
        "Epa": epa,
        "Ipa": ipa,
        "QC_Status": qc_status,
        "data": df # Return dataframe for plotting
    }