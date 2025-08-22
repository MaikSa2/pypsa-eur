import pypsa
#import numpy as np
#import pandas as pd
import os

# Netzwerkpfad anpassen
eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/02/networks/base_s_20___2050.nc"

# Netzwerk laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

# Generatoren mit "hsat" im Carrier entfernen
hsat_mask = n.generators.carrier.str.contains("hsat", case=False, na=False)
removed_generators = n.generators[hsat_mask]

n.generators = n.generators[~hsat_mask]

print(f"{len(removed_generators)} Generator(en) mit 'hsat' im Carrier entfernt.")

# Suffix "_nohsat" für Backup-Datei
base, ext = os.path.splitext(eur_file)
eur_file_backup = base + "_pre_041_hsat_removal" + ext

# Netzwerk speichern
n.export_to_netcdf(eur_file)
n_copy.export_to_netcdf(eur_file_backup)

print(f"Geändertes Netzwerk gespeichert unter:\n{eur_file}")
print(f"Backup des ursprünglichen Netzwerks gespeichert unter:\n{eur_file_backup}")
