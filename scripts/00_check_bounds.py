import pypsa
import pandas as pd

# Konfiguration
MAX_CAPACITY_MW = 1e6   # z. B. 1.000.000 MW = 1000 GW
MAX_STORAGE_MWH = 1e7   # Speichergrenze
REPORT_ONLY = True      # True = nur melden, False = automatisch anpassen

# Netzwerk laden
path = r"/home/student_01/Student_Folders/Maik/pypsa-eur/results/04/networks/base_s_20___2050.nc" 
n = pypsa.Network(path)

def check_bounds(df, colname, limit, name):
    if colname in df.columns:
        too_large = df[df[colname] > limit]
        if not too_large.empty:
            print(f"\n{name} mit zu großen Bounds (> {limit}):")
            print(too_large[[colname]])
            if not REPORT_ONLY:
                df.loc[df[colname] > limit, colname] = limit
                print(f"  → Werte auf {limit} gesetzt")

# Generatoren
check_bounds(n.generators, "p_nom_max", MAX_CAPACITY_MW, "Generatoren")

# Speicher
check_bounds(n.storage_units, "p_nom_max", MAX_CAPACITY_MW, "Storage Units Leistung")
check_bounds(n.storage_units, "max_hours", MAX_STORAGE_MWH, "Storage Units Kapazität (max_hours)")

# Stores (Energiespeicher ohne Leistung)
check_bounds(n.stores, "e_nom_max", MAX_STORAGE_MWH, "Stores Kapazität")

# Links (z. B. Übertragungsleitungen, Konverter)
check_bounds(n.links, "p_nom_max", MAX_CAPACITY_MW, "Links")

# Optional: angepasstes Netz speichern
if not REPORT_ONLY:
    path_new = r"/home/student_01/Student_Folders/Maik/pypsa-eur/results/04/networks/base_s_20___2050_fixes.nc" 
    n.export_to_netcdf(path_new)
    print("\nGespeichertes Netz: base_s_20___2050_fixed.nc")

print("\n✅ Bound-Check abgeschlossen.")
