from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Descriptors import MolWt, MolLogP

def get_molecule_image(smiles):
    """
    Takes a SMILES string and returns a PIL image of the molecule.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        return Draw.MolToImage(mol, size=(300, 300))
    return None

def get_molecule_properties(smiles):
    """
    Calculates basic properties useful for formulation.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        return {
            "Molecular Weight": f"{MolWt(mol):.2f} g/mol",
            "LogP (Hydrophobicity)": f"{MolLogP(mol):.2f}"
        }
    return {}