import kagglehub
import h5py
import os
import glob
import streamlit as st

def inspect_group(name, obj):
    """Helper to print structure of HDF5 groups"""
    if isinstance(obj, h5py.Group):
        return f"📁 Group: {name} (Keys: {list(obj.keys())})"
    elif isinstance(obj, h5py.Dataset):
        return f"🔢 Dataset: {name} (Shape: {obj.shape})"
    return f"❓ Other: {name}"

def fetch_and_process_kaggle_data(num_cycles=1):
    st.info("🕵️ STARTING STRUCTURE INSPECTION...")
    
    # 1. Download
    try:
        path = kagglehub.dataset_download("rickandjoe/mit-battery-degradation-dataset/versions/1")
    except Exception as e:
        return f"Download Error: {e}"

    # 2. Find File
    mat_files = glob.glob(os.path.join(path, "**", "*.mat"), recursive=True)
    if not mat_files:
        return "No .mat files found."
    
    target_file = mat_files[0]
    filename = os.path.basename(target_file)
    st.success(f"📂 Found file: {filename}")

    try:
        with h5py.File(target_file, 'r') as f:
            # LEVEL 1: Top Level
            st.markdown("### 1. Top Level Keys")
            st.write(list(f.keys()))
            
            if 'batch' not in f:
                return "❌ Error: 'batch' group not found."
            
            batch = f['batch']
            
            # LEVEL 2: Batch Keys (Cells)
            st.markdown("### 2. Batch Keys (First 5)")
            keys = list(batch.keys())
            st.write(keys[:5])
            
            # Pick first cell
            first_cell = keys[0] # likely 'b1c0'
            st.markdown(f"### 3. Inside Cell '{first_cell}'")
            cell_group = batch[first_cell]
            st.write(list(cell_group.keys()))
            
            if 'cycles' not in cell_group:
                return "❌ Error: 'cycles' key not found in cell."

            # LEVEL 3: Cycles
            cycles_dset = cell_group['cycles']
            st.write(f"Cycles Dataset Shape: {cycles_dset.shape}")
            
            # Get a reference to a cycle
            # Try index 10
            ref = None
            try:
                # Try different shapes
                if cycles_dset.ndim == 2:
                    ref = cycles_dset[10][0] # standard (N, 1)
                    if not ref: ref = cycles_dset[0][10] # transposed (1, N)
                else:
                    ref = cycles_dset[10]
            except:
                st.warning("⚠️ Could not grab index 10, trying index 0...")
                ref = cycles_dset[0][0] if cycles_dset.ndim == 2 else cycles_dset[0]

            # LEVEL 4: Inside a Cycle (THE CRITICAL PART)
            st.markdown("### 4. 🚨 INSIDE ONE CYCLE (LOOK HERE!)")
            try:
                cycle_group = f[ref]
                
                # PRINT EVERYTHING INSIDE THE CYCLE
                # This will tell us if it's 'V', 'Voltage', 'data', etc.
                keys_inside = list(cycle_group.keys())
                st.error(f"🔑 FOUND KEYS: {keys_inside}")
                
                # Drill down one more level just in case
                for k in keys_inside:
                    item = cycle_group[k]
                    if isinstance(item, h5py.Group):
                        st.write(f"   ↳ Inside '{k}': {list(item.keys())}")
                        
            except Exception as e:
                st.error(f"Could not dereference cycle: {e}")

    except Exception as e:
        return f"Global Error: {e}"

    return "Inspection Complete. Look at the keys above."

if __name__ == "__main__":
    st.write("Run from app.py")