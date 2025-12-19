# Seismik Kanti Wattwil

Einfache Software um Daten auszuwerten, die mit der Seismik-Apparatur der Kanti Wattwil aufgenommen wurden. Die Software beschränkt sich auf den Fall einer horizontalen Schicht mit P-Wellengeschwindigkeit `v1` und Dicke `d1` über einem Halbraum mit P-Wellengeschwindigkeit `v2`. 

André Nuber, ISME St. Gallen, 12.2025

mithilfe von claude.ai

Stand 19.12.2025: eine laufende Version, die noch viel Luft nach oben hat. 

Ideen für die Weiterentwicklung: siehe todo.md

## Bedienungsanleitung

### Voraussetzungen

Benötigt werden: 
- [ ] eine aktuelle Python-Installation (3.12.3 oder neuer)
- [ ] Pakete matplotlib, pandas, numpy, math

Das Programm wurde bisher nur mit VS Code ausgeführt. 

### Daten darstellen

Die Main-Methode von `plot_seismogram.py` beginnt mit der Angabe des Dateinamens. Setze dort (Zeile 145) den Pfad zu deiner Datei. Direkt darunter gibst du den Geophon-Abstand in Metern an. Die restlichen benötigten Angaben werden aus dem Header deiner Daten herausgelesen. 

Führe `plot_seismogram.py` aus. Ziehe das Fenster so zurecht, dass du einen klaren Blick auf die Daten erhältst. Verwende die Zoom-Funktion bei Bedarf. 

### Parameter extrahieren 

#### P-Wellengeschwindigkeit

Wenn du die Daten nach deinem Wunsch dargestellt hast, drücke `x`. Nun kannst du per Mausklick zwei Punkte im Seismogramm zu einer Geraden verbinden. Versuche damit, die Ersteinsätze so gut wie möglich zu erwischen. Das Programm gibt im Terminal die Geradengleichung und die P-Wellengeschwindigkeit aus. Entscheide, ob es sich dabei um `v1` oder `v2` handelt. 

#### Crossover-Distanz

Eine Gerade zu bestimmen ist nur einmalig möglich. Schliesse das Seismogramm (drücke `q`) und starte das Programm neu, wenn du eine zweite Geradengleichung bestimmen möchtest. Die Crossover-Position dem entspricht dem `x`-Wert des Schnittpunkts zweier Geraden -- eine für die direkte Welle, eine für die refraktierte. Diesen musst du selbst berechnen. Achtung: 

**Achtung**: 
- Die Position `x` steht im Seismogramm auf der y-Achse. Du kannst die Crossover-Position -- wenn überhaupt -- auf der y-Achse ablesen. 
- Die Crossover-Position entspricht im Allgemeinen noch *nicht* der Crossover-Distanz. 
Die Crossover-Distanz `xc` entspricht dem Abstand zwischen Shot-Position und Crossover-Position. Auch diese musst du manuell berechnen. 

Für die Schichtdicke `d1` der oberen Schicht gilt: 

`d1 = 1/2 * xc * math.sqrt( (v2-v1)/(v2+v1) )`

Bis anhin übernimmt das Programm diese Rechnung noch nicht. Hier ist noch viel Handarbeit gefragt. 

## Dokumentation

ab Zeile | Was geschieht da? 
------ | -----------------
10 | Lowpass-Filter um hochfrequentes Rauschen zu unterdrücken
27 | `read_metadata(...)` liest alle relevanten Parameter aus den Kopfzeilen der .csv
73 | `linear_function(...)`: Gerade durch zwei Punkte bestimmen
88 | `on_key(...)` steuert die Reaktionen auf Tastendrücke
98 | `on_click(...)` steuert die Reaktionen auf Mausklicks (nach Aktivieren mit `x`)
123 | Geradengleichung berechnen und ausgeben
145 | Dateiname und Geophon-Abstand manuell einstellen
148 | `read_metadata(...)` wird aufgerufen
155 | Liste für die Zeit aufsetzen
165 | einzelne Seismogramm-Spuren bearbeiten. Korrekturen: Nullinie, Normalisieren, an gewünschten Ort verschieben
171 | Filtermöglichkeiten: gewünschten Filter einkommentieren und Parameter wählen
174 | ... und zeichnen
177 | Tastendruck und Mausklick registrieren, Gerade darstellen