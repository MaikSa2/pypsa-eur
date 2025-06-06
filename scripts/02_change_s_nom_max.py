import pypsa
import numpy as np

# Eingabe- und Ausgabedateien
eur_file = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\merged_network_2050_newlines.nc"

# Netzwerk laden
n_eur = pypsa.Network(eur_file)

# Alle 'inf'-Werte in 's_nom_max' durch 20000 ersetzen
mask_inf = np.isinf(n_eur.lines["s_nom_max"])
n_eur.lines.loc[mask_inf, "s_nom_max"] = 20000.0

# Netzwerk speichern
n_eur.export_to_netcdf(output_file)

print(f"Netzwerk erfolgreich gespeichert unter:\n{output_file}")
