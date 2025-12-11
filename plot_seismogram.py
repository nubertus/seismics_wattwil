""" Seismogramme aus der Wattwiler Apparatur plotten. 

    André Nuber, 12.2025
"""
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np

def fft_lowpass(y, fs, cutoff):
    n = len(y)
    Y = np.fft.rfft(y)
    freqs = np.fft.rfftfreq(n, d=1/fs)
    Y[freqs > cutoff] = 0
    y_filt = np.fft.irfft(Y, n)
    return y_filt

def read_metadata(file): 
    """
    liest die Kopfzeilen und extrahiert die wichtigsten Werte
    
    Args: 
        input_file: Pfad zur CSV-Datei

    Returns: 
        Ein Tuple mit: 
        - pre_trigger_scan_count
        - post_trigger_scan_count 
        - scan_rate
        - trigger_time (string)
        - dt: sampling rate
        - n: Anzahl Messdaten pro Spur 
        - num_header_lines
    """
    # Anzahl Kopfzeilen automatisch ermitteln (bis "Scan Number" gefunden wird)
    header_lines = []
    num_header_lines = 0
    with open(input_file, 'r', encoding='latin-1') as f:
        for i, line in enumerate(f):
            stripped_line = line.strip()
            if stripped_line.startswith("Scan Number"):
                num_header_lines = i
                break
            header_lines.append(stripped_line)
    
    print(f"Anzahl Kopfzeilen: {num_header_lines}")
    
    # Metadaten extrahieren
    metadata = {}
    for line in header_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    print("Metadaten:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
        
    pre_trigger_scan_count = int(metadata.get("Pre-Trigger Scan Count", "1000")) # hinteres Argument: Standardwert
    post_trigger_scan_count = int(metadata.get("Post-Trigger Scan Count", "3000"))
    scan_rate = int(metadata.get("Post-Trigger Scan Rate(Hz)", "4000"))
    trigger_time = metadata.get("Trigger Time", "dd.mm.yyyy hh:mm:ss")

    return pre_trigger_scan_count, post_trigger_scan_count, scan_rate, trigger_time, num_header_lines

def on_key(event):
    """Tastendruck: 'x' = Start, 'q' = Quit"""
    if event.key == 'x':
        state['selection_active'] = True
        state['clicks'] = []
        ax.set_title("Klicke 2 Punkte (oder 'q' zum Abbrechen)")
        print("Punkt-Auswahl aktiviert. Klicke 2 Punkte...")
        fig.canvas.draw()
    elif event.key == 'q':
        plt.close()

def on_click(event):
    """Click registrieren, wenn Auswahl aktiv ist."""
    if not state['selection_active'] or event.inaxes != ax:
        return
    
    if len(state['clicks']) >= 2:
        return
    
    x, y_val = event.xdata, event.ydata
    state['clicks'].append((x, y_val))
    
    # Visual Feedback
    ax.plot(x, y_val, 'ro', markersize=5)
    fig.canvas.draw()
    
    print(f"Punkt {len(state['clicks'])}: ({x:.4f}, {y_val:.4f})")
    
    if len(state['clicks']) == 2:
        state['selection_active'] = False
        ax.set_title(f"Fertig! Punkte: {state['clicks']}")
        print(f"Beide Punkte ausgewählt: {state['clicks']}")

if __name__ == "__main__":
    input_file = "2025-12-06/log00058.csv"
    spacing = 2         # Geophon Abstand in Metern

    pre_trigger_scan_count, post_trigger_scan_count, scan_rate, trigger_time, num_header_lines = read_metadata(input_file)

    # Daten einlesen (ab der Zeile nach den Kopfzeilen)
    data = pd.read_csv(input_file, skiprows=num_header_lines, encoding='latin-1')
    data.columns = ["Scan Number", "Scan Time", "AI0", "AI1", "AI2", "AI3", "AI4", "AI5", "AI6", "AI7"] # Spaltennamen
    # print(data.head(10))

    dt = 1/scan_rate
    tmin = -pre_trigger_scan_count*dt
    tmax = post_trigger_scan_count*dt-dt
    n = pre_trigger_scan_count + post_trigger_scan_count
    t = np.linspace(tmin, tmax, n)

    fig, ax = plt.subplots()
    
    for i in range(8):
        column_name = "AI" + str(i)
        y = np.asarray(data[column_name].values)
        y -= np.median(y)   # Nulllinie korrigieren 
        y /= max(y)         # Normalisieren
        y += i*spacing      # Spuren im Seismogramm versetzt zeichnen
        
        # mögliche Filter: (1) moving average, (2) lowpass
        # y = pd.Series(y).rolling(window=10, center=True).mean().to_numpy()
        # y = fft_lowpass(y, scan_rate, cutoff=100)
        
        ax.plot(t,y,color="blue")

    state = {'selection_active': False, 'clicks': []}
    clicks = []
    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()
    print("Gespeicherte Punkte:", clicks)
    