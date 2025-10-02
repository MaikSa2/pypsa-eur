import os
import pypsa
import pandas as pd

from aa_run_variables import eur_file
# === Parameter ===
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" #r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
alg_file = r"/home/student_01/Student_Folders/Maik/elec_s_16_ec_lcopt_3h_manual.nc" #r"/home/student_01/Student_Folders/Maik/pypsa-earth/networks/01/elec_s_10_ec_lcopt_1h.nc" #r"C:\Users\maiks\pypsa-earth\networks\NoSectorNetwork\elec_s_6_ec_lcopt_Co2L0.00.nc"
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

print("n_alg snapshots:",n_alg.snapshots)
print("n_eur snapshots:", n_eur.snapshots)

def copy_components_and_timeseries(n_src, n_dst, only=None):
    """
    Kopiert Stammdaten (z.B. n.generators, n.links, …) und Zeitreihen (z.B. n.generators_t.p_max_pu, …)
    von n_src nach n_dst. Wenn `only` gesetzt ist (Liste mit z.B. ["generators","links"]),
    werden nur diese Komponenten übertragen.
    """

    # --- 1) Snapshots angleichen (wichtig für _t-Tabellen) ---
    # Übernimmt auch die Snapshot-Gewichtungen
    n_dst.set_snapshots(n_src.snapshots, n_src.snapshot_weightings)

    # --- 2) Reihenfolge: Carrier → Buses → Rest ---
    components = list(n_src.components.keys())
    if only is not None:
        components = [c for c in components if c in only]

    # Carriers zuerst (falls genutzt)
    ordered = []
    if "carriers" in components:
        ordered.append("carriers")
    if "buses" in components:
        ordered.append("buses")
    ordered += [c for c in components if c not in ("carriers", "buses")]

    # --- 3) Stammdaten kopieren ---
    for comp in ordered:
        df = getattr(n_src, comp)
        if df.empty:
            continue

        # Beispiel: Wenn du Busnamen verändern willst (z.B. Suffix anfügen),
        # dann hier die bus-Spalten anfassen, bevor du add() machst.

        for name, row in df.iterrows():
            # row ist eine Series mit den Attributen der Komponente
            kwargs = row.dropna().to_dict()
            n_dst.add(comp[:-1].capitalize(), name=name, **kwargs)
            # comp[:-1].capitalize(): "generators" → "Generator", "links" → "Link", …

    # --- 4) Zeitreihen kopieren ---
    # Alle *_t-Container in n_src, die es auch in n_dst gibt
    # Beispiel: "generators_t", "links_t", "loads_t", "storage_units_t", "stores_t", …
    for attr in dir(n_src):
        if not attr.endswith("_t"):
            continue
        if not hasattr(n_dst, attr):
            continue

        ts_src = getattr(n_src, attr)
        ts_dst = getattr(n_dst, attr)

        # Jede DataFrame-Variable im *_t-Namespace übertragen
        for key in dir(ts_src):
            if key.startswith("_"):
                continue
            val = getattr(ts_src, key)
            if isinstance(val, pd.DataFrame):
                # Spalten auf Schnittmenge begrenzen (nur bereits hinzugefügte Assets)
                cols = [c for c in val.columns if c in getattr(n_dst, attr[:-2]).index]
                if not cols:
                    continue

                # Snapshots ausrichten (zur Sicherheit reindexen)
                df_aligned = val.reindex(index=n_dst.snapshots, columns=cols)

                # Zuweisung in Zielnetz
                setattr(ts_dst, key, df_aligned.copy())

copy_components_and_timeseries(n_alg, n_eur) # only=["generators", "links"]

'''
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
'''

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