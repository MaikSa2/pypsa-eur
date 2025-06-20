import os
import pypsa
import pandas as pd

# === Parameter ===
eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/01/networks/base_s_20___2050.nc" #r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
alg_file = r"/home/student_01/Student_Folders/Maik/pypsa-earth/networks/01/elec_s_10_ec_lcopt_1h.nc" #r"C:\Users\maiks\pypsa-earth\networks\NoSectorNetwork\elec_s_6_ec_lcopt_Co2L0.00.nc"
#output_file = "merged_europe_algeria_2050.nc"

# === Netzwerke laden ===
n_eur = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

n_alg = pypsa.Network(alg_file)

n_alg.component
#display(n_eur_copy.component)
n_eur.component

n_alg.lines.rename(lambda x: f"DZ_{x}", inplace=True)
n_alg.lines

# === Algerische Komponenten hinzufügen ===
for component in n_alg.components.keys():
    df = getattr(n_alg, component)

    if df.empty:
        continue  # Keine Daten vorhanden

    # === Busspalten anpassen ===
    #for col in df.columns:
     #   if col.startswith("bus") and df[col].dtype == object:
      #      df[col] = df[col] + " alg"

    # === Hinzufügen mit n.add() ===
    for i, row in df.iterrows():
        n_eur.add(component, name=i, **row.dropna().to_dict())

# === Lines aus n_alg extrahieren ===
lines = n_alg.lines.copy()

# === Busspalten anpassen ===
#lines["bus0"] = lines["bus0"] + " alg"
#lines["bus1"] = lines["bus1"] + " alg"

# === Zeilenweise hinzufügen ===
for name, row in lines.iterrows():
    try:
        n_eur.add("Line", name=name, **row.dropna().to_dict())
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Line '{name}': {e}")


n_eur_copy = pypsa.Network(eur_file)

print(n_alg.component)
print(n_eur_copy.component)
print(n_eur.component)



target_buses = n_eur.buses[
    (n_eur.buses.x == -5.5) & (n_eur.buses.y == 46.0)
].index

bus_sizes = pd.Series(0.1, index=n_eur.buses.index)  # Default-Wert für alle Busse
bus_sizes.loc[target_buses] = 0.0  # Ausblenden dieser Busse

links_to_hide = n_eur.links.filter(like="bus").isin(target_buses).any(axis=1)
link_widths = pd.Series(2.0, index=n_eur.links.index)
link_widths[links_to_hide] = 0.2

lines_to_hide = (
    (n_eur.lines.bus0.isin(target_buses)) |
    (n_eur.lines.bus1.isin(target_buses))
)
line_widths = pd.Series(5.0, index=n_eur.lines.index)
line_widths[lines_to_hide] = 0.0

n_eur.plot(
    bus_sizes=bus_sizes,
    line_widths=line_widths,
    link_widths=link_widths
)


# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre01" + ext

#output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\merged_network_2050.nc"
n_eur.export_to_netcdf(eur_file)
n_eur_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter: {eur_file}")