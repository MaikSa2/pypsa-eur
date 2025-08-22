import pypsa
import linopy
import gurobipy as gp
from gurobipy import GRB

# Dein gespeichertes Netzwerk laden:
path = r"/home/student_01/Student_Folders/Maik/pypsa-eur/results/04/networks/base_s_20___2050.nc" 
n = pypsa.Network(path)

# Model bauen
m =  n.optimize.create_model() # Linopy LP-Model
gm = m.to_gurobipy()  # Jetzt gurobipy.Model Objekt
#gm = m.backend  # gurobipy.Model Objekt

import gurobipy as gp

# Angenommen, dein Modell heißt `m`
# 1. Setze ein triviales Ziel (z. B. 0), damit Gurobi keine Optimierung macht
gm.setObjective(0.0, gp.GRB.MINIMIZE)

# 2. Nutze die eingebaute Feasibility Relaxation:
#    - relaxobjtype = 0 → minimiere Summe der Verletzungen
#    - minrelax = True → suche minimal verletzte Lösung

#Penalty-Listen für Feasibility Relaxation erstellen
lbpen = [1.0] * gm.NumVars     # Strafe für Untergrenzen-Verletzung
ubpen = [1.0] * gm.NumVars     # Strafe für Obergrenzen-Verletzung
rhspen = [1.0] * gm.NumConstrs # Strafe für Nebenbedingungs-Verletzung
relaxmodel = gm.feasRelax(0, True, lbpen, ubpen, rhspen, None, None, None) #relaxobjtype=0, minrelax=True

# 3. Lösen (nur auf Machbarkeit)
relaxmodel.Params.TimeLimit = 300  # z.B. 5 Minuten
relaxmodel.optimize()

# 4. Prüfen
if relaxmodel.status == gp.GRB.OPTIMAL:
    print("✅ Modell ist machbar (ggf. mit minimalen Verletzungen).")
elif relaxmodel.status == gp.GRB.INFEASIBLE:
    print("❌ Modell ist unmachbar.")
else:
    print(f"⚠️ Solver-Status: {relaxmodel.status}")
