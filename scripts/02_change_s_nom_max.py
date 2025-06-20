import pypsa
import numpy as np
import os

# Eingabe- und Ausgabedateien
eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/01/networks/base_s_20___2050.nc"  #r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
#output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\merged_network_2050_newlines.nc"

# Netzwerk laden
n_eur = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

# Alle 'inf'-Werte in 's_nom_max' durch 20000 ersetzen
mask_inf = np.isinf(n_eur.lines["s_nom_max"])
n_eur.lines.loc[mask_inf, "s_nom_max"] = 20000.0

# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre02" + ext

# Netzwerk speichern
n_eur.export_to_netcdf(eur_file)
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
