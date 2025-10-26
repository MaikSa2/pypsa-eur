import os
import pypsa
import pandas as pd
import math

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

for attr in dir(n_alg):
    if not attr.endswith("_t") or not hasattr(n_eur, attr):
        continue

    ts_src = getattr(n_alg, attr)
    ts_dst = getattr(n_eur, attr)

    base_comp = attr[:-2]  # "generators_t" -> "generators"
    if not hasattr(n_eur, base_comp):
        continue
    existing_assets = getattr(n_eur, base_comp).index

    for key in dir(ts_src):
        if key.startswith("_"):
            continue
        val = getattr(ts_src, key)
        if not isinstance(val, pd.DataFrame):
            continue

        # nur Assets, die im Ziel existieren
        cols = [c for c in val.columns if c in existing_assets]
        if not cols:
            continue

        new_df = val.reindex(index=n_eur.snapshots, columns=cols)

        # --- Update-in-Place statt Ersetzen ---
        old_df = getattr(ts_dst, key, None)
        if isinstance(old_df, pd.DataFrame):
            # Index vereinheitlichen
            old_df = old_df.reindex(index=n_eur.snapshots)

            # Spaltenvereinigung (alles Alte behalten)
            all_cols = old_df.columns.union(new_df.columns)
            old_df = old_df.reindex(columns=all_cols)

            # Werte aus Quelle aufschreiben (nur überlappende Zellen)
            old_df.loc[new_df.index, new_df.columns] = new_df

            setattr(ts_dst, key, old_df)
        else:
            # gab es noch nicht → neu anlegen
            setattr(ts_dst, key, new_df)

n_eur.lines.loc[["DZ_1", "DZ_9"], "s_nom_extendable"] = False

links_to_remove = [
    "H2 pipeline DZ0 0-MA0 2",
    "H2 pipeline DZ0 0-MA0 2-reversed",
    "H2 pipeline DZ0 5-MA0 2",
    "H2 pipeline DZ0 5-MA0 2-reversed"
]

for link in links_to_remove:
    if link in n_eur.links.index:
        n_eur.remove("Link", link)

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

"""
n_eur.plot(
    bus_sizes=bus_sizes,
    line_widths=line_widths,
    link_widths=link_widths
)
"""

def haversine_o(lon1, lat1, lon2, lat2):
    """
    Berechnet die Distanz (in km) zwischen zwei Punkten
    auf der Erde mit der Haversine-Formel.
    """
    R = 6371.0  # Erdradius in km

    # Umwandlung in Radiant
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def distances_for_pairs(pairs, points, factor=1.0):
    """pairs: [(bus0,bus1), ...], points: {bus: (lon,lat)}"""
    d = {}
    for a, b in pairs:
        lon1, lat1 = points[a]
        lon2, lat2 = points[b]
        d[f"{a} -> {b}"] = factor * haversine_o(lon1, lat1, lon2, lat2)
    return d

def add_links_elec_routing_new_H2_pipelines():
        attrs = ["bus0", "bus1", "length"]
        h2_links = pd.DataFrame(columns=attrs)

        candidates = pd.concat(
            {
                "lines": n_eur.lines[attrs],
                "links": n_eur.links.loc[n_eur.links.carrier == "DC", attrs],
            }
        )

        my_buses = [("DZ5 0", "DZ0 3"), ("MR3 0", "MR2 0"),("DZ5 0", "DZ0 0"), ("MR2 0", "MR6 0")]  # optional: drittes Feld = Länge
        points = {bus: (row.x, row.y) for bus, row in n_eur.buses.iterrows()}
        dists = distances_for_pairs(my_buses, points, factor=1.25)

        my_buses_with_length = []
        for bus0, bus1 in my_buses:
            key = f"{bus0} -> {bus1}"
            length = dists[key]  # Länge aus deinem Dictionary holen
            my_buses_with_length.append((bus0, bus1, length))

        for b in my_buses_with_length:
            # erlaubt (bus0, bus1) oder (bus0, bus1, length)
            if len(b) == 2:
                bus0, bus1 = b
                length = 100.0  # setz hier deinen Default
            else:
                bus0, bus1, length = b

            buses = [bus0, bus1]
            buses.sort()
            name = f"H2 pipeline {buses[0]} -> {buses[1]}"

            if name not in h2_links.index:
                h2_links.at[name, "bus0"] = buses[0]
                h2_links.at[name, "bus1"] = buses[1]
                h2_links.at[name, "length"] = length

        

        n_eur.madd(
            "Link",
            h2_links.index,
            bus0=h2_links.bus0.values + " H2",
            bus1=h2_links.bus1.values + " H2",
            p_min_pu=-1,
            p_nom_extendable=True,
            length=h2_links["length"].astype(float).values,#h2_links.length.values,
            capital_cost= 29.669828144872003 * h2_links["length"].astype(float).values,#h2_links.length.values
            carrier="H2 pipeline",
            lifetime= 50   #costs.at["H2 (g) pipeline", "lifetime"],
        )

add_links_elec_routing_new_H2_pipelines()


# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre01" + ext

#output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\merged_network_2050.nc"
n_eur.export_to_netcdf(eur_file)
n_eur_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter: {eur_file}")