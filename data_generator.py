import numpy as np
import pickle
import os

def generate_synthetic_battery_data(num_cells=50):
    """
    Generates a synthetic dataset mimicking the Severson/MIT structure.
    Output: A dictionary of battery cells saved as a pickle file.
    """
    
    # Ensure the Data folder exists
    if not os.path.exists('Data'):
        os.makedirs('Data')
        
    batch_data = {}
    
    print(f"Generating {num_cells} synthetic battery cells...")
    
    for i in range(num_cells):
        cell_id = f"b1c{i}"
        
        # 1. Simulate Cycle Life (The Target)
        # Randomly assign 'Good' (>1200 cycles) or 'Bad' (<800 cycles)
        is_high_life = np.random.choice([True, False])
        
        if is_high_life:
            cycle_life = np.random.randint(1200, 2000)
            degradation_rate = 0.0001  # Very slow fade
        else:
            cycle_life = np.random.randint(400, 800)
            degradation_rate = 0.002   # Fast fade
            
        # 2. Simulate Voltage Curves (Vdlin)
        # We simulate 150 cycles. Shape: (1000 voltage points, 150 cycles)
        # This allows us to calculate Q100 - Q10 later.
        
        n_cycles = 150
        n_points = 1000
        vdlin = np.zeros((n_points, n_cycles))
        
        # Base curve (Open Circuit Voltage shape - Sigmoid-ish)
        x = np.linspace(0, 1, n_points)
        base_curve = 3.0 + 1.2 / (1 + np.exp(-10 * (x - 0.5)))
        
        for cycle in range(n_cycles):
            # Apply degradation:
            # As cycles increase, voltage sags (resistance increases)
            # Bad batteries sag MUCH faster.
            sag = degradation_rate * cycle * np.random.uniform(0.8, 1.2)
            
            # Add some sensor noise
            noise = np.random.normal(0, 0.002, n_points)
            
            # Cycle 0 is fresh, Cycle N is degraded
            # The curve shifts DOWN over time
            vdlin[:, cycle] = base_curve - sag + noise

        # 3. Pack into Dictionary Structure
        # This matches the structure expected by your analysis script
        batch_data[cell_id] = {
            "cycle_life": np.array([[cycle_life]]), # Double brackets to mimic MATLAB structure
            "Vdlin": vdlin,
            "summary": {"IR": np.random.uniform(0.01, 0.02, n_cycles)} # Simulated Internal Resistance
        }

    # 4. Save to Pickle
    file_path = os.path.join('Data', 'batch1.pkl')
    with open(file_path, 'wb') as f:
        pickle.dump(batch_data, f)
        
    print(f"✅ Success! Generated 'Data/batch1.pkl' with {num_cells} cells.")
    print("You can now run your Electro-Insight analysis script.")

if __name__ == "__main__":
    generate_synthetic_battery_data()