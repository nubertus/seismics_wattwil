""" Diese Python-Datei dient dazu, die Schlagpositionen 
    und den Geophon-Abstand richtig zu wählen. 
    
    André Nuber, 12.2025
"""
n_geophones = 8     # Anzahl Geophone
v1 = 350    # erwartete Geschwindigkeit (in m/s) Schicht 1 (Erdboden)
v2 = 1500   # erwartete Geschwindigkeit (in m/s) Schicht 2 (Wasserspiegel/Festgestein)
d1 = 3      # erwartete Schichtdicke 1 (in m)

xc = 2*d1 / ((v2-v1)/(v2+v1))**0.5  # Crossover-Distanz
dx = 2*xc/n_geophones     # Geophon-Abstand

print(f"Als Crossover-Distanz ist {xc:.1f} m zu erwarten. ")
print(f"Die Geophone können z. B. alle {dx:.0f} m platziert werden. ")
if dx >= 4:
    print("ACHTUNG: Auf diese Distanz kann nur bei (sehr) günstigen Bedingungen")
    print("noch ein Signal aufgezeichnet werden. ")