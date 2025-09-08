import pypsa
import numpy as np
import pandas as pd
import os

from aa_run_variables import eur_file

# Eingabe- und Ausgabedateien
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" 
#output_file_old = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050_pre05.nc"

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

#Platzhalter für den relevanten Code
#H2 Pipeline
n.add("Link",
          "H2 pipeline DZ0 1 -> IT0 0",
          bus0="TN0 0 H2",
          bus1="IT0 0 H2",
          carrier="H2 pipeline",
          efficiency=1.0,
          length=1443.403468068955, #berechnet mit costs.ipynb
          reversed = False, #0.0, evtl. kann ich so vermeiden dass beim SOlven dieser Fehler auftritt, mit "bool" und "float"
          capital_cost = 49231.76026618799, #berechnet mit costs.ipynb
          #capital_cost=costs.at["H2 (g) pipeline", "capital_cost"],
          p_nom_extendable=True,
          lifetime=50,
          )


# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre05" + ext

# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk mit Pipeline erfolgreich gespeichert unter:\n{eur_file}")
