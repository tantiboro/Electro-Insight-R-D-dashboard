import pandas as pd
import numpy as np
import os

def create_batch_data(num_files=10):
    if not os.path.exists('data'):
        os.makedirs('data')

    print(f"Generating {num_files} synthetic CV scan files...")

    for i in range(num_files):
        # 1. Simulate Potential
        forward = np.linspace(-0.5, 1.0, 500)
        backward = np.linspace(1.0, -0.5, 500)
        potential = np.concatenate([forward, backward])

        # 2. Simulate Two Categories (Chemometrics Use Case)
        # First half of files are "Good", second half are "Contaminated"
        if i < num_files / 2:
            category = "Standard"
            peak_pos = 0.40  # Standard location
            noise_level = 0.1
        else:
            category = "Contaminated"
            peak_pos = 0.48  # Shifted peak (the anomaly)
            noise_level = 0.25 # More noisy

        # Peak Generation
        peak_variance = np.random.uniform(9, 11)
        ox_peak = peak_variance * np.exp(-((potential - peak_pos)**2) / 0.05)
        red_peak = -peak_variance * np.exp(-((potential - (peak_pos - 0.1))**2) / 0.05)
        
        background = 0.5 * potential
        noise = np.random.normal(0, noise_level, len(potential))
        current = ox_peak + red_peak + background + noise

        # 3. Save
        df = pd.DataFrame({"Potential_V": potential, "Current_uA": current})
        filename = f"data/Run_{i}_{category}.csv"
        df.to_csv(filename, index=False)

if __name__ == "__main__":
    create_batch_data()