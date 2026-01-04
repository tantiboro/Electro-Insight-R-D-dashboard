import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import os

# 1. Page Configuration
st.set_page_config(page_title="Electro-Insight", page_icon="🔋", layout="wide")

st.title("🔋 Electro-Insight: Battery Intelligence")
st.markdown("### Optimized for Early Prediction of Battery Cycle Life")

# 2. Load Data (Cached for performance)
@st.cache_data
def load_data():
    file_path = os.path.join('Data', 'batch1.pkl')
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

data = load_data()

if data is None:
    st.error("❌ Data file not found! Please run 'python data_generator.py' first.")
    st.stop()

# 3. Sidebar: Global Stats & Controls
st.sidebar.header("Dataset Overview")
total_cells = len(data)
st.sidebar.metric("Total Batteries", total_cells)

# Extract Cycle Lives for statistics
all_lives = []
cell_ids = list(data.keys())

for uid in cell_ids:
    # Handle the nested array structure from the generator
    life = data[uid]['cycle_life'].flatten()[0]
    all_lives.append(life)

avg_life = int(np.mean(all_lives))
st.sidebar.metric("Avg Cycle Life", f"{avg_life} cycles")

# 4. Main Dashboard - Visualizing the Physics
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution of Battery Life")
    fig_hist, ax_hist = plt.subplots()
    ax_hist.hist(all_lives, bins=20, color='skyblue', edgecolor='black')
    ax_hist.set_xlabel("Cycle Life (Total Cycles)")
    ax_hist.set_ylabel("Count")
    ax_hist.set_title("Dataset Balance")
    st.pyplot(fig_hist)

with col2:
    st.subheader("Variance Analysis (Delta-Q)")
    st.info("Visualizing the difference between Cycle 100 and Cycle 10.")
    
    # Calculate Delta V for all cells
    fig_var, ax_var = plt.subplots()
    
    # Color map
    norm = plt.Normalize(min(all_lives), max(all_lives))
    cmap = plt.cm.turbo
    
    count_plotted = 0
    for uid in cell_ids:
        vdlin = data[uid]['Vdlin']
        life = data[uid]['cycle_life'].flatten()[0]
        
        # Check if we have enough data (at least 100 cycles)
        if vdlin.shape[1] > 100:
            # Calculate Q100 - Q10 (Voltage difference)
            # Generator shape is (1000 points, 150 cycles)
            # Columns are cycles.
            delta = vdlin[:, 99] - vdlin[:, 9]
            
            ax_var.plot(delta, color=cmap(norm(life)), alpha=0.6, linewidth=0.5)
            count_plotted += 1

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax_var)
    cbar.set_label('Cycle Life')
    
    ax_var.set_xlabel("Discharge Capacity Index")
    ax_var.set_ylabel("Voltage Difference (V)")
    st.pyplot(fig_var)

# 5. Deep Dive: Individual Cell Inspector
st.markdown("---")
st.subheader("🔍 Individual Cell Inspector")

selected_cell = st.selectbox("Select a Battery ID:", cell_ids)

if selected_cell:
    cell_data = data[selected_cell]
    this_life = cell_data['cycle_life'].flatten()[0]
    
    st.write(f"**Selected Cell:** {selected_cell}")
    st.write(f"**True Cycle Life:** {this_life} cycles")
    
    # Plot Voltage curves for this specific cell
    fig_cell, ax_cell = plt.subplots(figsize=(10, 4))
    
    vdlin = cell_data['Vdlin']
    # Plot Cycle 10 and Cycle 100
    ax_cell.plot(vdlin[:, 9], label="Cycle 10 (Fresh)", color='green')
    if vdlin.shape[1] > 99:
        ax_cell.plot(vdlin[:, 99], label="Cycle 100 (Degraded)", color='red', linestyle='--')
    
    ax_cell.set_title(f"Discharge Voltage Curves: {selected_cell}")
    ax_cell.legend()
    ax_cell.set_ylabel("Voltage (V)")
    ax_cell.set_xlabel("Discharge Index")
    st.pyplot(fig_cell)