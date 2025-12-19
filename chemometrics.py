import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- SNV Calculation Function ---
def apply_snv(data_matrix):
    """
    Standard Normal Variate (SNV) transformation.
    """
    row_means = np.mean(data_matrix, axis=1, keepdims=True)
    row_stds = np.std(data_matrix, axis=1, keepdims=True)
    row_stds[row_stds == 0] = 1
    return (data_matrix - row_means) / row_stds

# --- UPDATED FUNCTION DEFINITION ---
# Note the new argument: use_snv=True
def run_pca_analysis(data_folder='data', use_snv=True):
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    if not files:
        return None

    # 1. Build Data Matrix
    data_matrix = []
    filenames = []
    
    for file in files:
        df = pd.read_csv(os.path.join(data_folder, file))
        data_matrix.append(df['Current_uA'].values)
        filenames.append(file)

    X = np.array(data_matrix)
    
    # 2. Apply SNV (If the checkbox is checked)
    if use_snv:
        X = apply_snv(X)
    
    # 3. Standardize and Run PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(X_scaled)

    # 4. Format Results
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['Filename'] = filenames
    pca_df['Batch_Type'] = pca_df['Filename'].apply(lambda x: "Contaminated" if "Contaminated" in x else "Standard")

    return pca_df, pca.explained_variance_ratio_