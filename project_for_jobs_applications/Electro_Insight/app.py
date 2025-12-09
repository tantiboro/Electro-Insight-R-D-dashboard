import streamlit as st
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import generator
import analyzer
import chemometrics 
import structure_viz # Import the new module

st.set_page_config(page_title="Electro-Insight", layout="wide")

st.title("⚡ Electro-Insight: MSD R&D Dashboard")

# Create Tabs to separate Single File Analysis from Batch Chemometrics
tab1, tab2, tab3 = st.tabs(["🔬 Single Experiment", "📊 Chemometrics", "🧪 Structure-Property"])

# --- SIDEBAR ---
st.sidebar.header("Data Pipeline")
if st.sidebar.button("Generate New Lab Data"):
    generator.create_batch_data(12) # Generate 12 files
    st.sidebar.success("New batch data generated!")

data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# --- TAB 1: SINGLE EXPERIMENT (Existing Logic) ---
with tab1:
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    if files:
        selected_file = st.selectbox("Select File:", files)
        file_path = os.path.join(data_folder, selected_file)
        results = analyzer.process_cv_file(file_path)
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Epa (Potential)", f"{results['Epa']:.3f} V")
        c2.metric("Ipa (Current)", f"{results['Ipa']:.2f} µA")
        c3.metric("QC Status", results['QC_Status'], 
                  delta_color="normal" if results['QC_Status']=="PASS" else "inverse")
        
        # Plot
        df = results['data']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Potential_V'], y=df['Current_uA'], name='Raw'))
        fig.add_trace(go.Scatter(x=df['Potential_V'], y=df['Smooth_Current'], name='Smoothed'))
        fig.update_layout(title=f"Scan: {selected_file}", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: CHEMOMETRICS (New Feature) ---
with tab2:
    st.markdown("### Principal Component Analysis (PCA) for Anomaly Detection")
    st.markdown("Use this tool to identify drifting batches or contamination across the entire dataset.")
    
    if st.button("Run PCA Model"):
        pca_results, variance = chemometrics.run_pca_analysis(data_folder)
        
        if pca_results is not None:
            # 1. Explanation of Variance
            st.info(f"Model explains {sum(variance)*100:.2f}% of the dataset variance.")
            
            # 2. PCA Scatter Plot
            fig_pca = px.scatter(pca_results, x='PC1', y='PC2', 
                                 color='Batch_Type', 
                                 hover_data=['Filename'],
                                 title="Batch Clustering Analysis",
                                 color_discrete_map={"Standard": "blue", "Contaminated": "red"})
            
            fig_pca.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig_pca, use_container_width=True)
            
            st.warning("""
            **Interpretation:** Points clustered together share similar electrochemical fingerprints. 
            Outliers (Red) indicate potential contamination or electrode fouling.
            """)
        else:
            st.error("No data found to analyze.")

with tab3:
    st.markdown("### Molecular Candidate Screening")
    st.markdown("Link chemical structure modifications to electrochemical performance.")

    # 1. Select a Candidate Molecule (Simulating MSD Reagents)
    # These are real SMILES for conductive polymer monomers
    candidates = {
        "Polythiophene (Standard)": "C1=CSC=C1",
        "Polypyrrole (High Conductivity)": "C1=CNC=C1",
        "PEDOT (High Stability)": "C1COCC2=C1SC=C2",
        "Ruthenium(bpy)3 (ECL Label)": "[Ru+2]12([N]3=CC=CC=C3C4=C1C=CC=N4)([N]5=CC=CC=C5C6=C2C=CC=N6)[N]7=CC=CC=C7C8=C(C=CC=N8)N1=CC=CC=C1"
    }
    
    selected_mol = st.selectbox("Select Formulation Candidate:", list(candidates.keys()))
    smiles_code = candidates[selected_mol]

    col_chem, col_data = st.columns([1, 2])

    with col_chem:
        st.subheader("Chemical Structure")
        # Draw the molecule using RDKit
        mol_img = structure_viz.get_molecule_image(smiles_code)
        if mol_img:
            st.image(mol_img, caption=f"SMILES: {smiles_code}")
        
        # Calculate Properties
        props = structure_viz.get_molecule_properties(smiles_code)
        st.table(props)

    with col_data:
        st.subheader("Predicted Electrochemical Behavior")
        # Here we simulate that different molecules have different CV shapes
        # In a real app, this would query a database based on the Structure ID
        
        if "Thiophene" in selected_mol:
            peak_v = 0.4
            current_mod = 1.0
        elif "Pyrrole" in selected_mol:
            peak_v = 0.2  # Oxidizes easier
            current_mod = 1.2 # Higher current
        elif "PEDOT" in selected_mol:
            peak_v = 0.1
            current_mod = 1.5 # Best performance
        else:
            peak_v = 0.8  # Ruthenium oxidizes at higher potential
            current_mod = 0.8
            
        # Generate a "Live" curve for this molecule
        # We reuse your generator logic but tweak it dynamically
        pot = list(np.linspace(-0.5, 1.2, 100))
        curr = [10 * current_mod * np.exp(-((p - peak_v)**2) / 0.05) + (0.5*p) + np.random.normal(0, 0.05) for p in pot]
        
        fig_mol = go.Figure()
        fig_mol.add_trace(go.Scatter(x=pot, y=curr, mode='lines', name=selected_mol, line=dict(color='green', width=3)))
        fig_mol.update_layout(title=f"Expected CV for {selected_mol}", xaxis_title="Potential (V)", yaxis_title="Current (µA)")
        st.plotly_chart(fig_mol, use_container_width=True)