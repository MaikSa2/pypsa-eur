import pandas as pd
'''

import searoute as sr

export_ports = {
    "DZ0_2":  {"x": 3.069,   "y": 36.763},   # Algiers
    "DZ0_5":  {"x": -0.63438,"y": 35.71487}, # Oran
    "MA0_0":  {"x": -7.617,  "y": 33.600},   # Casablanca
    "MA0_1":  {"x": -5.798,  "y": 35.764},   # Tanger
    "MR6_0":  {"x": -15.965, "y": 18.079},   # Nouakchott
    "TN0_0":  {"x": 10.165,  "y": 36.8108}   # Tunis
}

import_ports = {
    "BE0_0": {"x": 4.404, "y": 51.219},   # Antwerpen
    "DE0_0": {"x": 9.993, "y": 53.551},   # Hamburg
    "DK0_0": {"x": 8.459, "y": 56.461},   # Esbjerg
    "ES0_0": {"x": -7.157, "y": 37.246},  # Huelva
    "FR0_0": {"x": 0.107, "y": 49.494},   # Le Havre
    "GB2_0": {"x": -0.217, "y": 53.586},  # Immingham
    "IE3_0": {"x": -6.260, "y": 53.349},  # Dublin
    "IT0_0": {"x": 13.769, "y": 45.649},  # Triest
    "NL0_0": {"x": 4.479, "y": 51.922},   # Rotterdam
    "NO1_0": {"x": 10.752, "y": 59.913},  # Oslo
    "PT0_0": {"x": -8.867, "y": 37.953},  # Sines
    "SE1_0": {"x": 11.966, "y": 57.708}   # Göteborg
}

shipping_distances = {}

# Alle Kombinationen durchlaufen
for exp_code, exp_coord in export_ports.items():
    for imp_code, imp_coord in import_ports.items():
        origin = [exp_coord["x"], exp_coord["y"]]
        destination = [imp_coord["x"], imp_coord["y"]]
        try:
            route = sr.searoute(origin, destination)
            dist = route.properties['length']
        except Exception as e:
            print(f"Fehler bei Route {exp_code} -> {imp_code}: {e}")
            dist = None
        # Tupel als Key
        shipping_distances[(exp_code, imp_code)] = dist


# Beispiel-Ausgabe
for k, v in shipping_distances.items():
    print(f"{k}: {v} km")
    
'''

# CSV einlesen
cost_df = pd.read_csv("shipping_costs.csv", sep=";", index_col=0)
if "Einheit" in cost_df.columns:
    cost_df = cost_df.drop(columns=["Einheit"])

cost_df.columns = cost_df.columns.astype(float)

def get_cost(km, energy):
    """
    km: Distanz in km
    energy: Energieträger (z.B. 'NH3' oder 'methanol')
    """
    if energy not in cost_df.index:
        raise ValueError(f"Energieträger {energy} nicht in CSV enthalten")
    
    # nächste größere Entfernung in den Spalten
    #col = cost_df.columns[cost_df.columns.get_indexer(km, method='bfill')]
    cols = cost_df.columns.astype(float)

    # km = deine Distanz
    col = cols[cols >= km].min() 
    return float(cost_df.loc[energy, col])


export_buses = ["DZ0 2", "DZ0 5", "MA0 0", "MA0 1", "MR6 0", "TN0 0"]
import_buses = ["BE0 0", "DE0 0", "DK0 0", "ES0 0", "FR0 0", "GB2 0","IE3 0", "IT0 0", "NL0 0", "NO1 0", "PT0 0", "SE1 0"]

shipping_distances = {
    ("DZ0 2 NH3", "BE0 0 NH3"): 3347.454741498388,
    ("DZ0 2 NH3", "DE0 0 NH3"): 3861.291195981269,
    ("DZ0 2 NH3", "DK0 0 NH3"): 3927.388109501628,
    ("DZ0 2 NH3", "ES0 0 NH3"): 1011.5833920263902,
    ("DZ0 2 NH3", "FR0 0 NH3"): 3025.2414180831997,
    ("DZ0 2 NH3", "GB2 0 NH3"): 3494.5973865010556,
    ("DZ0 2 NH3", "IE3 0 NH3"): 3110.466771210713,
    ("DZ0 2 NH3", "IT0 0 NH3"): 2422.3648623699323,
    ("DZ0 2 NH3", "NL0 0 NH3"): 3401.9497750166265,
    ("DZ0 2 NH3", "NO1 0 NH3"): 4320.384197352705,
    ("DZ0 2 NH3", "PT0 0 NH3"): 1306.9435948241478,
    ("DZ0 2 NH3", "SE1 0 NH3"): 4192.408580399795,
    ("DZ0 5 NH3", "BE0 0 NH3"): 3017.7187079372998,
    ("DZ0 5 NH3", "DE0 0 NH3"): 3531.5551624201807,
    ("DZ0 5 NH3", "DK0 0 NH3"): 3597.65207594054,
    ("DZ0 5 NH3", "ES0 0 NH3"): 681.8473584653013,
    ("DZ0 5 NH3", "FR0 0 NH3"): 2695.5053845221114,
    ("DZ0 5 NH3", "GB2 0 NH3"): 3164.861352939967,
    ("DZ0 5 NH3", "IE3 0 NH3"): 2780.7307376496237,
    ("DZ0 5 NH3", "IT0 0 NH3"): 2777.78943675346,
    ("DZ0 5 NH3", "NL0 0 NH3"): 3072.213741455538,
    ("DZ0 5 NH3", "NO1 0 NH3"): 3990.6481637916177,
    ("DZ0 5 NH3", "PT0 0 NH3"): 977.2075612630588,
    ("DZ0 5 NH3", "SE1 0 NH3"): 3862.6725468387062,
    ("MA0 0 NH3", "BE0 0 NH3"): 2555.3631063959356,
    ("MA0 0 NH3", "DE0 0 NH3"): 3069.1995608788166,
    ("MA0 0 NH3", "DK0 0 NH3"): 3135.2964743991756,
    ("MA0 0 NH3", "ES0 0 NH3"): 419.06322156646763,
    ("MA0 0 NH3", "FR0 0 NH3"): 2233.149782980747,
    ("MA0 0 NH3", "GB2 0 NH3"): 2702.505751398603,
    ("MA0 0 NH3", "IE3 0 NH3"): 2318.3751361082595,
    ("MA0 0 NH3", "IT0 0 NH3"): 3518.4674322984474,
    ("MA0 0 NH3", "NL0 0 NH3"): 2609.858139914174,
    ("MA0 0 NH3", "NO1 0 NH3"): 3528.2925622502535,
    ("MA0 0 NH3", "PT0 0 NH3"): 514.8519597216948,
    ("MA0 0 NH3", "SE1 0 NH3"): 3400.316945297342,
    ("MA0 1 NH3", "BE0 0 NH3"): 2499.3841134403274,
    ("MA0 1 NH3", "DE0 0 NH3"): 3013.220567923208,
    ("MA0 1 NH3", "DK0 0 NH3"): 3079.317481443567,
    ("MA0 1 NH3", "ES0 0 NH3"): 163.51276396832907,
    ("MA0 1 NH3", "FR0 0 NH3"): 2177.1707900251386,
    ("MA0 1 NH3", "GB2 0 NH3"): 2646.526758442995,
    ("MA0 1 NH3", "IE3 0 NH3"): 2262.3961431526523,
    ("MA0 1 NH3", "IT0 0 NH3"): 3181.4709542407804,
    ("MA0 1 NH3", "NL0 0 NH3"): 2553.879146958566,
    ("MA0 1 NH3", "NO1 0 NH3"): 3472.313569294645,
    ("MA0 1 NH3", "PT0 0 NH3"): 458.8729667660865,
    ("MA0 1 NH3", "SE1 0 NH3"): 3344.3379523417334,
    ("MR6 0 NH3", "BE0 0 NH3"): 4057.3368608425,
    ("MR6 0 NH3", "DE0 0 NH3"): 4571.17331532538,
    ("MR6 0 NH3", "DK0 0 NH3"): 4637.270228845741,
    ("MR6 0 NH3", "ES0 0 NH3"): 2110.08792392648,
    ("MR6 0 NH3", "FR0 0 NH3"): 3735.1235374273115,
    ("MR6 0 NH3", "GB2 0 NH3"): 4204.479505845167,
    ("MR6 0 NH3", "IE3 0 NH3"): 3798.499187528935,
    ("MR6 0 NH3", "IT0 0 NH3"): 5243.982572014615,
    ("MR6 0 NH3", "NL0 0 NH3"): 4111.831894360738,
    ("MR6 0 NH3", "NO1 0 NH3"): 5030.266316696817,
    ("MR6 0 NH3", "PT0 0 NH3"): 2163.697088079329,
    ("MR6 0 NH3", "SE1 0 NH3"): 4902.290699743908,
    ("TN0 0 NH3", "BE0 0 NH3"): 4015.11451089009,
    ("TN0 0 NH3", "DE0 0 NH3"): 4528.95096537297,
    ("TN0 0 NH3", "DK0 0 NH3"): 4595.0478788933315,
    ("TN0 0 NH3", "ES0 0 NH3"): 1679.2431614180919,
    ("TN0 0 NH3", "FR0 0 NH3"): 3692.9011874749012,
    ("TN0 0 NH3", "GB2 0 NH3"): 4162.2571558927575,
    ("TN0 0 NH3", "IE3 0 NH3"): 3778.126540602414,
    ("TN0 0 NH3", "IT0 0 NH3"): 1786.651506209694,
    ("TN0 0 NH3", "NL0 0 NH3"): 4069.6095444083285,
    ("TN0 0 NH3", "NO1 0 NH3"): 4988.043966744407,
    ("TN0 0 NH3", "PT0 0 NH3"): 1974.6033642158495,
    ("TN0 0 NH3", "SE1 0 NH3"): 4860.068349791498
}

#print(shipping_distances)