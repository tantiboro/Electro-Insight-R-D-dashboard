import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_pca_analysis(data_folder='data'):
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    if not files:
        return None

    # 1. Build the Data Matrix (Features = Current at each potential step)
    data_matrix = []
    filenames = []
    
    for file in files:
        df = pd.read_csv(os.path.join(data_folder, file))
        # We flatten the current array to use it as features
        # Assumption: All files have same length (guaranteed by our generator)
        data_matrix.append(df['Current_uA'].values)
        filenames.append(file)

    X = np.array(data_matrix)
    
    # 2. Standardize (Z-score normalization)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Apply PCA
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(X_scaled)

    # 4. Create Result DataFrame
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['Filename'] = filenames
    
    # Extract "Category" from filename for coloring (Quick hack for visualization)
    pca_df['Batch_Type'] = pca_df['Filename'].apply(lambda x: "Contaminated" if "Contaminated" in x else "Standard")

    explained_variance = pca.explained_variance_ratio_
    
    return pca_df, explained_variance