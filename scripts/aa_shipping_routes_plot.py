import pandas as pd
import numpy as np

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

# 1) Rumpfpfad (lon, lat)

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
'''
trunk_ll = [
    (-15.98, 18.08), (-17.5, 21.0), (-15.0, 27.0), (-11.5, 31.5),
    (-10.0, 36.5), (-9.3, 38.7), (-9.5, 42.8), (-6.0, 46.5),
    (-4.8, 48.5), (-2.0, 50.0), (1.5, 51.0), (3.5, 52.5), (6.5, 53.7)
]
'''
# 2) Ports (lon, lat). Keys müssen exakt zu deinen Link-Namen passen.
ports = {
    "MR6 0 H2 to DE0 0 H2 shipping-lh2": (8.11, 53.52),    # Wilhelmshaven
    "MR6 0 H2 to FR0 0 H2 shipping-lh2": (0.11, 49.49),    # Le Havre
    "MR6 0 H2 to IE3 0 H2 shipping-lh2": (-6.26, 53.35),   # Dublin
    "MR6 0 H2 to GB2 0 H2 shipping-lh2": (1.31, 51.96),    # Felixstowe
    "MR6 0 H2 to DK0 0 H2 shipping-lh2": (8.43, 55.47),    # Esbjerg
    "MR6 0 H2 to ES0 0 H2 shipping-lh2": (-3.00, 43.30),   # Bilbao
    "MR6 0 H2 to IT0 0 H2 shipping-lh2": (8.93, 44.41),    # Genova
    "MR6 0 H2 to NL0 0 H2 shipping-lh2": (4.29, 51.94),    # Rotterdam
    "MR6 0 H2 to NO1 0 H2 shipping-lh2": (5.33, 60.39),    # Bergen
    "MR6 0 H2 to PT0 0 H2 shipping-lh2": (-9.14, 38.72),   # Lissabon
    "MR6 0 H2 to SE1 0 H2 shipping-lh2": (11.95, 57.70),   # Göteborg
}

# 3) Spurzuteilung und Spurabstand
lane_index = {k: i for k, i in zip(ports.keys(), [-3, -2, -1, 0, 1, 2, -5, 3, 4, -4, 5   ])}  # links/rechts im Kanal
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

# 5) Bauen der paths
trunk_xy = to_xy(trunk_ll)
paths = {}
for key, port_ll in ports.items():
    d = lane_index[key] * lane_spacing_m
    lane_xy = offset_polyline(trunk_xy, d)
    path_xy = branch_path(lane_xy, port_ll)
    paths[key] = [(float(lon), float(lat)) for lon, lat in to_ll(path_xy)]