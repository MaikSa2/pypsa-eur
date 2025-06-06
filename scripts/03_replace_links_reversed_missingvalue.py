import pypsa
import numpy as np
import pandas as pd

# Eingabe- und Ausgabedateien
eur_file = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\fixed_network_2050_reversed_fixed.nc"

# Netzwerk laden
n = pypsa.Network(eur_file)

# 'reversed' Spalte prüfen und fehlende Werte ersetzen
if "reversed" in n.links.columns:
    n.links["reversed"] = n.links["reversed"].fillna(False).astype(bool)
else:
    n.links["reversed"] = False

# Netzwerk speichern
n.export_to_netcdf(output_file)

print(f"Netzwerk erfolgreich gespeichert unter:\n{output_file}")
