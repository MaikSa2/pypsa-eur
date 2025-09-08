import pypsa
import numpy as np
import pandas as pd
import os

from aa_run_variables import eur_file

# Eingabe- und Ausgabedateien
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" 

# Netzwerk laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

# 'reversed' Spalte prüfen und fehlende Werte ersetzen
if "reversed" in n.links.columns:
    n.links["reversed"] = n.links["reversed"].fillna(False).astype(bool)
else:
    n.links["reversed"] = False

# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre03" + ext

# Netzwerke speichern
n.export_to_netcdf(eur_file)
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
