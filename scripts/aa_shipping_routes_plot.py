import pandas as pd
import numpy as np
from collections import defaultdict

paths = {
    "MR6 0 H2 to DE0 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.3, 38.7),     # off Lisbon
        (-9.5, 42.8),     # Cape Finisterre
        (-6.0, 46.5),     # Bay of Biscay
        (-4.8, 48.5),     # off Brittany (Ushant)
        (-2.0, 50.0),     # English Channel
        (1.5, 51.0),      # Strait of Dover
        (3.5, 52.5),      # Dutch coast
        (6.5, 53.7),      # German Bight
        (8.11, 53.52),    # Wilhelmshaven
    ],
    "MR6 0 H2 to FR0 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.3, 38.7),     # off Lisbon
        (-9.5, 42.8),     # Cape Finisterre
        (-6.0, 46.5),     # Bay of Biscay
        (-4.8, 48.5),     # off Brittany (Ushant)
        (-3.5, 47.7),     # south Brittany
        (-2.5, 48.7),     # approach Channel
        (-1.5, 49.2),     # Normandy coast
        (0.11, 49.49),    # Le Havre (FR0 0 proxy)
    ],
}

paths.update({
    # Irland: Dublin
    "MR6 0 H2 to IE3 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.5, 42.8),     # Cape Finisterre
        (-10.5, 45.5),    # N-Atlantic
        (-10.0, 49.5),    # Celtic Sea
        (-9.0, 51.5),     # S of Ireland
        (-8.5, 52.5),     # SW Ireland
        (-7.5, 53.0),     # St George's Channel
        (-6.8, 53.3),     # Dublin Bay approaches
        (-6.26, 53.35),   # Dublin
    ],

    # Großbritannien: Felixstowe (Ostküste)
    "MR6 0 H2 to GB2 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.3, 38.7),     # off Lisbon
        (-9.5, 42.8),     # Cape Finisterre
        (-6.0, 46.5),     # Bay of Biscay
        (-4.8, 48.5),     # off Brittany
        (-2.0, 50.0),     # English Channel
        (0.5, 51.2),      # Thames approaches
        (1.1, 51.6),      # S North Sea
        (1.31, 51.96),    # Felixstowe
    ],

    # Dänemark: Esbjerg
    "MR6 0 H2 to DK0 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.3, 38.7),     # off Lisbon
        (-9.5, 42.8),     # Cape Finisterre
        (-6.0, 46.5),     # Bay of Biscay
        (-4.8, 48.5),     # off Brittany
        (-2.0, 50.0),     # English Channel
        (1.5, 51.0),      # Dover Strait
        (4.0, 53.0),      # Dutch coast
        (6.5, 53.7),      # German Bight
        (7.5, 54.5),      # N of Helgoland
        (8.43, 55.47),    # Esbjerg
    ],

    # Spanien: Bilbao
    "MR6 0 H2 to ES0 0 H2 shipping-lh2": [
        (-15.98, 18.08),  # Nouakchott
        (-17.5, 21.0),
        (-15.0, 27.0),
        (-11.5, 31.5),
        (-10.0, 36.5),
        (-9.5, 42.8),     # Cape Finisterre
        (-7.5, 43.2),     # Bay of Biscay W
        (-6.0, 43.5),     # Bay of Biscay mid
        (-4.5, 43.45),    # approach Bilbao
        (-3.0, 43.30),    # Bilbao
    ],
})

from pyproj import Transformer
import re

# 1) Rumpfpfad (lon, lat)
"""
trunk_ll = [
    (-17.5, 18.0),  # weiter westlich vor Mauretanien
    (-20.0, 23.0),
    (-21.0, 28.0),
    (-20.0, 33.0),
    (-17.5, 36.0),  # weit vor Iberien
    (-14.0, 39.0),
    (-12.0, 42.0),
    (-10.5, 44.5),
    (-9.0, 46.5),
    (-7.0, 48.5),
    (-5.0, 49.7),
    (-2.0, 50.0),   # Eingang Ärmelkanal
    (1.5, 51.0),
    (3.5, 52.5),
    (6.5, 53.7),
]
"""
'''
trunk_ll = [
    (-15.98, 18.08), (-17.5, 21.0), (-15.0, 27.0), (-11.5, 31.5),
    (-10.0, 36.5), (-9.3, 38.7), (-9.5, 42.8), (-6.0, 46.5),
    (-4.8, 48.5), (-2.0, 50.0), (1.5, 51.0), (3.5, 52.5), (6.5, 53.7)
]
'''

# ---------- 1) Zwei Trunks definieren ----------
trunk_ll_mr6 = [
    (-17.5, 18.0),    # vor Mauretanien
    (-20.0, 23.0),
    (-23.5, 30.0),    # neuer Punkt (aus Google Maps, umgedreht!)
    (-21.0, 40.0),
    (-18.0, 43.0),    # westlich Iberien
    (-14.0, 46.0),    # Golf von Biskaya (offshore)
    (-10.5, 48.0),    # westlich Bretagne
    (-7.5, 49.0),     # Annäherung Ärmelkanal
    (-4.5, 50.0),     # südlich England / Bretagne
    (-1.0, 51.0),     # Ärmelkanal-Mitte
    (2.0, 52.0),      # Doverstraße
    (4.0, 52.7),      # südliche Nordsee
    (6.0, 53.5),      # Helgoland / Borkum – Endpunkt
]



trunk_ll_dz05 = [
    (-0.62, 35.7),    # Oran (Start)
    (-2.0, 36.0),     # Alboranmeer
    (-5.5, 36.0),     # Straße von Gibraltar
    (-8.0, 36.5),     # Südportugiesische Küste
    (-10.0, 37.5),    # Westlich Algarve
    (-11.0, 39.0),    # vor Lissabon
    (-11.5, 40.5),    # mittlerer Atlantik auf Höhe Porto
    (-11.0, 42.5),    # vor Galicien
    (-9.5, 44.5),     # Golf von Biskaya (westlicher Bogen)
    (-7.0, 46.0),     # mittlere Biskaya
    (-4.5, 47.5),     # Bretagne
    (-2.5, 49.0),     # Ärmelkanal-Einfahrt
    (0.0, 50.0),      # südlich England
    (2.0, 51.0),      # Dover-Straße
    (4.0, 52.0),      # südliche Nordsee
    (6.0, 53.5),      # Borkum / Helgoland – Endpunkt
]

trunk_ll_dz02 = [
    (3.06, 36.75),    # Algier (Start)
    (1.2, 36.4),      # westliches Mittelmeer
    (-1.5, 36.1),     # Alboranmeer
    (-4.0, 36.0),     # Annäherung Gibraltar (Ost)
    (-5.5, 36.0),     # Straße von Gibraltar (Engstelle)
    (-7.8, 36.5),     # SW-Iberien / Algarve
    (-9.8, 37.6),     # westlich Algarve
    (-11.0, 39.0),    # Höhe Lissabon (offshore)
    (-11.6, 40.6),    # westl. Porto
    (-11.1, 42.5),    # vor Galicien
    (-9.6, 44.4),     # westlicher Biskaya-Bogen
    (-7.1, 46.0),     # mittlere Biskaya
    (-4.6, 47.4),     # Bretagne
    (-2.6, 49.0),     # Ärmelkanal-Einfahrt
    (0.0, 50.0),      # südlich England
    (2.0, 51.0),      # Dover-Straße
    (4.0, 52.0),      # südliche Nordsee
    (6.0, 53.5),      # Borkum/Helgoland – Endpunkt
]

# Casablanca ~ (-7.62, 33.60)
trunk_ll_ma00 = [
    (-7.62, 33.60),  # Casablanca (Start)
    (-9.0, 33.8),    # vor Marokko (offshore)
    (-10.5, 34.8),   # N-Atlantik vor Rabat
    (-11.5, 36.2),   # W-Algarve / Golf von Cádiz (offshore)
    (-11.4, 38.4),   # Höhe Lissabon (westlich)
    (-11.3, 40.2),   # westlich Porto
    (-10.8, 42.2),   # vor Galicien
    (-9.2, 44.4),    # Biskaya (westlicher Bogen)
    (-7.0, 46.0),    # mittlere Biskaya
    (-4.6, 47.5),    # Bretagne
    (-2.6, 49.0),    # Ärmelkanal-Einfahrt
    (0.0, 50.0),     # südlich England
    (2.0, 51.0),     # Dover-Straße
    (4.0, 52.0),     # südliche Nordsee
    (6.0, 53.5),     # Borkum/Helgoland – Endpunkt
]

# Agadir ~ (-9.60, 30.42)
trunk_ll_ma01 = [
    (-9.60, 30.42),  # Agadir (Start)
    (-10.8, 31.6),   # vor Marokko (weiter draußen)
    (-11.6, 33.2),   # N-Atlantik
    (-11.7, 35.2),   # W-Marokko/NW-Sahara offshore
    (-11.6, 37.8),   # westlich Algarve/Lissabon
    (-11.4, 39.8),   # westlich Porto
    (-10.9, 42.1),   # vor Galicien
    (-9.3, 44.3),    # Biskaya (westlicher Bogen)
    (-7.0, 46.0),    # mittlere Biskaya
    (-4.6, 47.5),    # Bretagne
    (-2.6, 49.0),    # Ärmelkanal-Einfahrt
    (0.0, 50.0),     # südlich England
    (2.0, 51.0),     # Dover-Straße
    (4.0, 52.0),     # südliche Nordsee
    (6.0, 53.5),     # Borkum/Helgoland – Endpunkt
]

# Tunis ~ (10.18, 36.80)
trunk_ll_tn00 = [
    (10.18, 36.80),   # Tunis (Start)
    (8.0, 36.7),      # Golf von Tunis
    (6.0, 36.5),      # Küste Algeriens
    (3.0, 36.3),      # Annäherung Algier
    (0.5, 36.1),      # westliches Mittelmeer
    (-2.0, 36.0),     # Alboranmeer
    (-4.5, 36.0),     # Straße von Gibraltar
    (-7.5, 36.4),     # Südportugiesische Küste
    (-9.5, 37.5),     # westlich Algarve
    (-11.0, 39.0),    # Höhe Lissabon (offshore)
    (-11.6, 40.6),    # westl. Porto
    (-11.0, 42.5),    # vor Galicien
    (-9.5, 44.4),     # Golf von Biskaya (westlicher Bogen)
    (-7.0, 46.0),     # mittlere Biskaya
    (-4.6, 47.5),     # Bretagne
    (-2.6, 49.0),     # Ärmelkanal-Einfahrt
    (0.0, 50.0),      # südlich England
    (2.0, 51.0),      # Dover-Straße
    (4.0, 52.0),      # südliche Nordsee
    (6.0, 53.5),      # Borkum / Helgoland – Endpunkt
]


# Zuordnung: Welche Gruppe benutzt welchen Trunk?
TRUNKS = {
    "MR6 0 H2": trunk_ll_mr6,
    "DZ0 5 H2": trunk_ll_dz05,
    "DZ0 2 H2": trunk_ll_dz02,
    "MA0 0 H2": trunk_ll_ma00,
    "MA0 1 H2": trunk_ll_ma01,
    "TN0 0 H2": trunk_ll_tn00,
}


# Basis-Ziele (einmal definieren)
destination_ports = {
    "DE0 0 H2": (8.11, 53.52),   # Wilhelmshaven
    "FR0 0 H2": (0.11, 49.49),   # Le Havre
    "IE3 0 H2": (-6.26, 53.35),  # Dublin
    "GB2 0 H2": (1.31, 51.96),   # Felixstowe
    "DK0 0 H2": (8.43, 55.47),   # Esbjerg
    "ES0 0 H2": (-3.00, 43.30),  # Bilbao
    "IT0 0 H2": (8.93, 44.41),   # Genova
    "NL0 0 H2": (4.29, 51.94),   # Rotterdam
    "NO1 0 H2": (5.33, 60.39),   # Bergen
    "PT0 0 H2": (-9.14, 38.72),  # Lissabon
    "SE1 0 H2": (11.95, 57.70),  # Göteborg
    "BE0 0 H2": (4.404, 51.219), # Antwerpen
}

# Alle Ursprungsgruppen, die es geben soll
origins = [
    "MR6 0 H2",
    "DZ0 5 H2",
    "DZ0 2 H2",
    "MA0 0 H2",
    "MA0 1 H2",
    "TN0 0 H2"
]

# Automatisch kombinieren
ports = {
    f"{origin} to {dest} shipping-lh2": coords
    for origin in origins
    for dest, coords in destination_ports.items()
}


# 3) Spurzuteilung und Spurabstand
#lane_index = {k: i for k, i in zip(ports.keys(), [-3, -2, -1, 0, 1, 2, -5, 3, 4, -4, 5   ])}  # links/rechts im Kanal
lane_spacing_m = 20000  # 20 km Abstand zwischen parallelen Routen

# 4) Projektion (Europa-LAEA in Meter)
tf_fwd = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
tf_inv = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)

def to_xy(ll):
    xs, ys = zip(*ll)
    X, Y = tf_fwd.transform(np.array(xs), np.array(ys))
    return np.column_stack([X, Y])

def to_ll(xy):
    X, Y = xy[:,0], xy[:,1]
    lon, lat = tf_inv.transform(X, Y)
    return list(zip(lon.tolist(), lat.tolist()))

def offset_polyline(xy, d):
    v = np.diff(xy, axis=0)                                   # Segmentvektoren
    L = np.linalg.norm(v, axis=1, keepdims=True).clip(1e-9)   # Längen
    n = np.column_stack([-v[:,1]/L[:,0], v[:,0]/L[:,0]])      # Linksnormale je Segment
    # Vertex-Normalen mit Miter-Join
    n_vert = np.vstack([n[0], (n[:-1] + n[1:]) / 2, n[-1]])
    n_vert /= np.linalg.norm(n_vert, axis=1, keepdims=True).clip(1e-9)
    return xy + d * n_vert

def branch_path(lane_xy, port_ll):
    px, py = tf_fwd.transform(port_ll[0], port_ll[1])
    port_xy = np.array([px, py])
    ib = int(np.argmin(np.linalg.norm(lane_xy - port_xy, axis=1)))
    path_xy = np.vstack([lane_xy[:ib+1], port_xy])
    return path_xy

# Neues #4

# ---------- 4) Gruppieren nach Ursprung ----------
# Gruppe = alles vor " to ", z.B. "MR6 0 H2" / "DZ0 5 H2"
def origin_group(key: str) -> str:
    return key.split(" to ")[0].strip()

ports_by_group = defaultdict(dict)
for k, v in ports.items():
    grp = origin_group(k)
    ports_by_group[grp][k] = v

# ---------- 5) Lane-Indizes je Gruppe ----------
# Wenn du feste Indizes wie früher willst, wiederverwende sie pro Gruppe:
base_indices = [-3, -2, -1, 0, 1, 2, -5, 3, 4, -4, 5]  # Länge 11

def assign_lane_indices(keys):
    keys = list(keys)
    if len(keys) <= len(base_indices):
        return {k: base_indices[i] for i, k in enumerate(keys)}
    # Falls mehr als 11 Ziele in der Gruppe: symmetrisch auffüllen
    idx = [0]
    k = 1
    while len(idx) < len(keys):
        idx += [k, -k]
        k += 1
    return {k: idx[i] for i, k in enumerate(keys)}

def cumulative_lengths(xy):
    v = np.diff(xy, axis=0)
    seglen = np.linalg.norm(v, axis=1)
    return np.concatenate([[0.0], np.cumsum(seglen)])

def smooth_taper(s, s0, halfwidth, floor=0.0):
    """
    Skaliert den seitlichen Offset entlang des Trunks:
    - 1 außerhalb des Fensters [s0-halfwidth, s0+halfwidth]
    - innen kosinusförmig runter bis 'floor' und wieder rauf
    """
    scale = np.ones_like(s)
    L = 2*halfwidth
    left, right = s0 - halfwidth, s0 + halfwidth
    win = (s >= left) & (s <= right)
    # normiert auf [0,1] innerhalb des Fensters
    x = np.zeros_like(s)
    x[win] = (s[win] - left) / L
    # Kosinus-Glocke: 1 -> floor -> 1
    #scale[win] = floor + (1 - floor) * 0.5 * (1 + np.cos(2*np.pi*(x[win] - 0.5)))
    # 1 an den Rändern (x=0,1), Minimum (=floor) in der Mitte (x=0.5)
    scale[win] = floor + (1 - floor) * 0.5 * (1 + np.cos(2*np.pi * x[win]))

    return scale

def offset_polyline_tapered(xy, d, scale):
    v = np.diff(xy, axis=0)
    L = np.linalg.norm(v, axis=1, keepdims=True).clip(1e-9)
    n = np.column_stack([-v[:,1]/L[:,0], v[:,0]/L[:,0]])
    n_vert = np.vstack([n[0], (n[:-1] + n[1:]) / 2, n[-1]])
    n_vert /= np.linalg.norm(n_vert, axis=1, keepdims=True).clip(1e-9)
    return xy + (d * scale)[:, None] * n_vert
# -----------------------------------------------------------------------------

paths = {}
for grp, grp_ports in ports_by_group.items():
    if grp not in TRUNKS:
        raise ValueError(f"Kein Trunk für Gruppe '{grp}' definiert.")

    trunk_xy = to_xy(TRUNKS[grp])

    # Lane-Indizes wie gehabt:
    lane_index = assign_lane_indices(grp_ports.keys())

    # Nur für DZ0 5 H2: Engstelle um Gibraltar
    if grp in ["DZ0 5 H2", "DZ0 2 H2", "TN0 0 H2"]:
        print(f"{grp} Zweig aktiviert!!!!!!")
    #if grp == "DZ0 5 H2":
        #print("DZ0 5 H2 Zweig aktiviert!!!!!!")
        # Längskoordinate entlang des Trunks
        s = cumulative_lengths(trunk_xy)

        # Gibraltar-Referenzpunkt (grob)
        gib_ll = (-5.5, 36.0)
        gx, gy = tf_fwd.transform(*gib_ll)
        gib_xy = np.array([gx, gy])

        # Index des nächstgelegenen Trunk-Punkts → s0
        ig = int(np.argmin(np.linalg.norm(trunk_xy - gib_xy, axis=1)))
        s0 = s[ig]

        # Breite und Restabstand der Engstelle
        halfwidth = 200e1   # 200 km links/rechts von s0
        floor     = 0.15    # min. 15% des normalen Abstands (0.0 = komplett zusammen)
        scale     = smooth_taper(s, s0, halfwidth, floor=floor)
        print("Scale im DZ0 5 Zweig:",scale)
    else:
        scale = None  # MR6 etc. ohne Taper
        print("Scale ohne Taper:",scale)

    # Spur bauen
    for key, port_ll in grp_ports.items():
        d = lane_index[key] * lane_spacing_m
        if scale is not None:
            lane_xy = offset_polyline_tapered(trunk_xy, d, scale)
            #print("offset_polyline_tapered wurde aufgerufen")
        else:
            lane_xy = offset_polyline(trunk_xy, d)
            #print("offset_polyline wurde aufgerufen")

        path_xy = branch_path(lane_xy, port_ll)
        paths[key] = [(float(lon), float(lat)) for lon, lat in to_ll(path_xy)]

#print("endültiges paths:", paths)
"""
# ---------- 6) Pfade bauen – pro Gruppe jeweils eigener Trunk ----------
paths = {}
for grp, grp_ports in ports_by_group.items():
    if grp not in TRUNKS:
        raise ValueError(f"Kein Trunk für Gruppe '{grp}' definiert. Definiere TRUNKS['{grp}']=trunk_ll_...")

    trunk_xy = to_xy(TRUNKS[grp])
    lane_index = assign_lane_indices(grp_ports.keys())

    for key, port_ll in grp_ports.items():
        d = lane_index[key] * lane_spacing_m
        lane_xy = offset_polyline(trunk_xy, d)
        path_xy = branch_path(lane_xy, port_ll)
        paths[key] = [(float(lon), float(lat)) for lon, lat in to_ll(path_xy)]
"""