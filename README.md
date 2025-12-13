# Seismik Kanti Wattwil

Einfache Software um Daten auszuwerten, die mit der Seismik-Apparatur der Kanti Wattwil aufgenommen wurden. Die Software beschränkt sich auf den Fall einer horizontalen Schicht mit P-Wellengeschwindigkeit `v1` und Dicke `d1` über einem Halbraum mit P-Wellengeschwindigkeit `v2`. 

André Nuber, ISME St. Gallen, 12.2025

## Bedienungsanleitung

### Daten darstellen

Die Main-Methode von `plot_seismogram.py` beginnt mit der Angabe des Dateinamens. Setze dort (Zeile 136) den Pfad zu deiner Datei. Direkt darunter gibst du den Geophon-Abstand in Metern an. Die restlichen benötigten Angaben werden aus dem Header deiner Daten herausgelesen. 

Führe `plot_seismogram.py` aus. Ziehe das Fenster so zurecht, dass du einen klaren Blick auf die Daten erhältst. Verwende die Zoom-Funktion bei Bedarf. 

### Parameter extrahieren 

#### P-Wellengeschwindigkeit

Wenn du die Daten nach deinem Wunsch dargestellt hast, drücke `x`. Nun kannst du per Mausclick zwei Punkte im Seismogramm zu einer Geraden verbinden. Versuche damit, die Ersteinsätze so gut wie möglich zu erwischen. Das Programm gibt im Terminal die Geradengleichung und die P-Wellengeschwindigkeit aus. Du musst selbst entscheiden, ob es sich dabei um `v1` oder `v2` handelt. 

#### Crossover-Distanz

Eine Gerade zu bestimmen ist nur einmalig möglich. Schliesse das Seismogramm (drücke `q`) und starte das Programm neu, wenn du eine zweite Geradengleichung bestimmen möchtest. Die Crossover-Position entspricht dem Schnittpunkt zweier Geraden - eine für die direkte Welle, eine für die refraktierte. Diesen musst du selbst berechnen. 

**Achtung**: Die Crossover-Position entspricht im Allgemeinen noch *nicht* der Crossover-Distanz. 
Die Crossover-Distanz `xc` entspricht dem Abstand zwischen Shot-Position und Crossover-Position. Auch diese musst du noch manuell berechnen. 



