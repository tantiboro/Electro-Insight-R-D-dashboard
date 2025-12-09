# structure_viz.py
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit.Chem.Descriptors import MolWt, MolLogP
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

def get_molecule_image(smiles):
    if not RDKIT_AVAILABLE:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            # Return the image object directly
            return Draw.MolToImage(mol, size=(300, 300))
    except Exception:
        return None
    return None

def get_molecule_properties(smiles):
    if not RDKIT_AVAILABLE:
        return {"Error": "RDKit library not loaded"}
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return {
                "Molecular Weight": f"{MolWt(mol):.2f} g/mol",
                "LogP (Hydrophobicity)": f"{MolLogP(mol):.2f}"
            }
    except Exception:
        return {"Error": "Calculation Failed"}
    return {}