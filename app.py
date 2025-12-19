import streamlit as st
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import generator
import analyzer
import chemometrics 
import structure_viz 

st.set_page_config(page_title="Electro-Insight", layout="wide")

st.title("⚡ Electro-Insight: MSD R&D Dashboard")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["🔬 Single Experiment", "📊 Chemometrics", "🧪 Structure-Property"])

# --- SIDEBAR ---
st.sidebar.header("Data Pipeline")
if st.sidebar.button("Generate New Lab Data"):
    generator.create_batch_data(12) 
    st.sidebar.success("New batch data generated!")

data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# --- TAB 1: SINGLE EXPERIMENT ---
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
    else:
        st.info("No data found. Please generate data using the sidebar.")

# --- TAB 2: CHEMOMETRICS (UPDATED WITH SNV TOGGLE) ---
with tab2:
    st.markdown("### Principal Component Analysis (PCA) for Anomaly Detection")
    st.markdown("Use this tool to identify drifting batches or contamination across the entire dataset.")
    
    # 1. NEW: Add the SNV Toggle Checkbox
    use_snv_toggle = st.checkbox("Apply SNV (Standard Normal Variate) Correction", value=True, 
                                 help="Normalizes signal intensity to focus analysis on peak shape rather than concentration.")

    if st.button("Run PCA Model"):
        # 2. UPDATE: Pass the toggle value to the function
        pca_results, variance = chemometrics.run_pca_analysis(data_folder, use_snv=use_snv_toggle)
        
        if pca_results is not None:
            # Explanation of Variance
            st.info(f"Model explains {sum(variance)*100:.2f}% of the dataset variance.")
            
            # PCA Scatter Plot
            # 3. UPDATE: Dynamic Title based on SNV status
            status_text = "On" if use_snv_toggle else "Off"
            
            fig_pca = px.scatter(pca_results, x='PC1', y='PC2', 
                                 color='Batch_Type', 
                                 hover_data=['Filename'],
                                 title=f"Batch Clustering Analysis (SNV={status_text})",
                                 color_discrete_map={"Standard": "blue", "Contaminated": "red"})
            
            fig_pca.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig_pca, use_container_width=True)
            
            st.warning("""
            **Interpretation:** Points clustered together share similar electrochemical fingerprints. 
            Outliers (Red) indicate potential contamination or electrode fouling.
            """)
        else:
            st.error("No data found to analyze.")

# --- TAB 3: STRUCTURE-PROPERTY ---
with tab3:
    st.markdown("### Molecular Candidate Screening")
    st.markdown("Link chemical structure modifications to electrochemical performance.")

    candidates = {
        "Polythiophene (Standard)": "C1=CSC=C1",
        "Polypyrrole (High Conductivity)": "C1=CNC=C1",
        "PEDOT (High Stability)": "C1COCC2=C1SC=C2",
        # UPDATE THIS LINE BELOW:
        "Ruthenium(bpy)3 (ECL Label)": "[Ru+2].c1ccc(nc1)c2ccccn2.c1ccc(nc1)c2ccccn2.c1ccc(nc1)c2ccccn2"
    }
    
    selected_mol = st.selectbox("Select Formulation Candidate:", list(candidates.keys()))
    smiles_code = candidates[selected_mol]

    col_chem, col_data = st.columns([1, 2])

    with col_chem:
        st.subheader("Chemical Structure")
        mol_img = structure_viz.get_molecule_image(smiles_code)
        if mol_img:
            st.image(mol_img, caption=f"SMILES: {smiles_code}")
        
        props = structure_viz.get_molecule_properties(smiles_code)
        st.table(props)

    with col_data:
        st.subheader("Predicted Electrochemical Behavior")
        
        if "Thiophene" in selected_mol:
            peak_v = 0.4; current_mod = 1.0
        elif "Pyrrole" in selected_mol:
            peak_v = 0.2; current_mod = 1.2 
        elif "PEDOT" in selected_mol:
            peak_v = 0.1; current_mod = 1.5 
        else:
            peak_v = 0.8; current_mod = 0.8
            
        pot = list(np.linspace(-0.5, 1.2, 100))
        curr = [10 * current_mod * np.exp(-((p - peak_v)**2) / 0.05) + (0.5*p) + np.random.normal(0, 0.05) for p in pot]
        
        fig_mol = go.Figure()
        fig_mol.add_trace(go.Scatter(x=pot, y=curr, mode='lines', name=selected_mol, line=dict(color='green', width=3)))
        fig_mol.update_layout(title=f"Expected CV for {selected_mol}", xaxis_title="Potential (V)", yaxis_title="Current (µA)")
        st.plotly_chart(fig_mol, use_container_width=True)