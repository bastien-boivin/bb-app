#%%
import pandas as pd

csv_file_path = r"C:\\Users\\basti\\Documents\\Output_HydroModPy\\LakeRes\\Reservoir\\Donnees journalieres EBR\\dam_input_2004_2024.csv"

df = pd.read_csv(csv_file_path, sep=";")
df["time"] = pd.to_datetime(df["time"], format="%d/%m/%Y")
df["ajout"] = df["canut"] + df["meu"]
df["prelevement"] = df["resti"] + df["usine"]
df["delta_anthropique"] = df["ajout"] - df["prelevement"]
df["delta_anthropique_sum"] = df["delta_anthropique"].cumsum()


Vmin = 1850000
Vmax = 14500000

df["natural"] = None  # initialisation

# On commence par affecter le volume initial le premier jour
df.loc[df.index[0], "natural"] = df.loc[df.index[0], "cheze_vol"]

# Boucle sur chaque jour (en partant du 2e, puisque le 1er est déjà défini)
for i in range(1, len(df)):
    current_day = df.index[i]
    previous_day = df.index[i-1]
    
    # Volume naturel de la veille
    nat_prev = df.at[previous_day, "natural"]
    
    # Variation réelle entre la veille et aujourd'hui
    delta = df.at[current_day, "cheze_vol"] - df.at[previous_day, "cheze_vol"]
    
    # On retire la part canut + meu
    delta_nat = delta - (df.at[current_day, "canut"] + df.at[current_day, "meu"])
    
    # Volume naturel avant seuil
    nat_before_thresh = nat_prev + delta_nat
    
    # Application des bornes
    if nat_before_thresh < Vmin:
        nat_today = Vmin
    elif nat_before_thresh > Vmax:
        nat_today = Vmax
    else:
        nat_today = nat_before_thresh
    
    # On stocke
    df.at[current_day, "natural"] = nat_today
    
print(df.head())
# %%
