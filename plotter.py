import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from pathlib import Path
import argparse
from matplotlib import cm
import copy
from typing import Tuple, List

# Utility functions
def load_csv(filepath: Path) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load CSV file into data and header arrays.
    """
    data = np.genfromtxt(filepath, dtype=str, delimiter=',', skip_header=11)
    header = np.genfromtxt(filepath, dtype=str, delimiter=',', max_rows=11)
    data = np.char.strip(data, '"')
    print(f'{filepath} loaded')
    return data, header

def movmean(signal: np.ndarray, window_size: int = 10) -> np.ndarray:
    """
    Calculate the moving mean of a signal using convolution.
    """
    return np.convolve(signal, np.ones(window_size) / window_size, mode='same')

def first_valid_point(signal: np.ndarray, threshold: float, start_idx: int = 0) -> int | None:
    """
    Find the first index in the signal where the value exceeds the threshold, starting from start_idx.
    """
    for idx in range(start_idx, len(signal)):
        if signal[idx] > threshold:
            return idx
    return None

def find_signal_start_indices(movmean_abs_signal: np.ndarray, averaged_derived_signal: np.ndarray, larger_threshold: float, smaller_threshold: float) -> Tuple[int | None, int | None, int | None]:
    """
    Find the first index of movmean_abs_signal above the larger threshold, then search within previous points for first above a smaller threshold, and lastly for a sign change in the derivative.

    """
    first_large_threshold_idx = first_valid_point(movmean_abs_signal, larger_threshold)
    search_range_1000 = max(0, first_large_threshold_idx - 1000)
    second_smaller_threshold_idx = first_valid_point(movmean_abs_signal, smaller_threshold, start_idx=search_range_1000)
    search_range_100 = max(0, second_smaller_threshold_idx - 100)
    third_sign_change_idx = None

    for idx in range(second_smaller_threshold_idx, search_range_100, -1):
        if np.sign(averaged_derived_signal[idx]) != np.sign(averaged_derived_signal[idx - 1]):
            third_sign_change_idx = idx
            break

    return first_large_threshold_idx, second_smaller_threshold_idx, third_sign_change_idx

# Plotting-related functions
def time_signals_plot_init(title: str, pretrigger: int) -> Tuple[plt.Figure, plt.Axes]:
    """
    Initialize the plot to show the signals of all geophons.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlabel('scan number')
    ax.set_ylabel('Geophon ID')
    ax.set_xlim(0.9*pretrigger, 6000)
    ax.set_ylim(-1, 9)
    ax.set_yticks(np.arange(8))
    ax.grid(axis='y')
    ax.set_title(title)
    plt.axvline(x=pretrigger, color='r', linestyle=':', label='Hammerschlag')

    # Dummy lines for legend
    ax.plot([float('nan')], [float('nan')], color='black', linestyle='-', label='Normalized Time Series')

    # ax.plot([float('nan')], [float('nan')], color='black', linestyle='--', label='Moving Mean Abs Signal')

    # ax.plot([float('nan')], [float('nan')], color='black', linestyle=':', label='Moving Mean Derived Signal')
    return fig, ax

def plot_single_signal(color: np.ndarray, signal_run_times: List[float], scannumber: np.ndarray, normalized_signals: List[np.ndarray], movmean_signals: List[np.ndarray], derived_signals: List[np.ndarray], ax: plt.Axes, i: int) -> None:
    """
    Plot a single signal on the given axis.
    """
    if signal_run_times[i] < 0 or np.isnan(signal_run_times[i]):
        ax.plot(scannumber, normalized_signals[i] + i, color='red', linewidth=1, marker='None', linestyle='-')
    else:
        ax.plot(scannumber, normalized_signals[i] + i, color=color, linewidth=0.5, marker='None', linestyle='-')
        # ax.plot(scannumber, movmean_signals[i] + i, color=color, linewidth=0.5,marker='None', linestyle='--')
        # ax.plot(scannumber, derived_signals[i] + i, color=color, linewidth=0.5, marker='None', linestyle=':')

def plotter(data: np.ndarray, header: np.ndarray, path: Path, filename: str) -> list[float]:
    """
    Plot the data from CSV file and detect signal starts based on user input or automatic detection.
    """
    pre_trigger = float(header[6].strip('Pre-Trigger Scan Count: '))
    scan_rate = float(header[7].strip('Pre-Trigger Scan Rate(Hz): '))
    names = data[0, 2:10]
    scannumber = np.linspace(0, 13000, 13000)
    data = data[2:, 2:10].astype(float)
    signal_run_times = [0] * 8
    fig, ax = time_signals_plot_init(
        'select manually points: RMB (set before trigger to ignore)',
        pre_trigger)

    # Initialize lists to save results
    signal_run_times = []
    derived_signals = []
    movmean_signals = []
    normalized_signals = []

    # Function to calculate moving mean using NumPy's convolution
    def movmean(signal, window_size=10):
        return np.convolve(signal, np.ones(window_size)/window_size, mode='same')

    # Set a colormap (e.g., 'viridis') for different colors
    cmap = cm.get_cmap('rainbow', len(names))

    for i in range(len(names)):
        # Calculate maximal amplitude of the signal
        max_signal = np.abs(np.max(data[:, i]))
        min_signal = np.abs(np.min(data[:, i]))
        delta = max(max_signal, min_signal)

        # Normalize the time series
        time_series_normalized = data[:, i] #/ (2*delta)
        normalized_signals.append(time_series_normalized)

        # Calculate the moving mean of the absolute signal
        movmean_abs_signal = movmean(np.abs(time_series_normalized))
        movmean_signals.append(movmean_abs_signal)

        # Calculate an approximative derivative
        derived_signal = np.diff(time_series_normalized)
        averaged_derived_signal = movmean(derived_signal, window_size = 3)
        averaged_derived_signal = np.pad(averaged_derived_signal, (0, 1), mode='edge')
        derived_signals.append(averaged_derived_signal)

        # estimate the signal starts, you may need manual corrections in some cases
        first_large_threshold_idx, second_smaller_threshold_idx, third_sign_change_idx = find_signal_start_indices(movmean_abs_signal, averaged_derived_signal, 0.2, 0.05)

        if third_sign_change_idx is None:
            signal_run_times.append(1000 * (second_smaller_threshold_idx - pre_trigger) / scan_rate)
        else:
            signal_run_times.append(1000 * (third_sign_change_idx - pre_trigger) / scan_rate)

        # Plotting the normalized time series with solid line and the moving mean with the same color but dashed line
        plot_single_signal(cmap(i), signal_run_times, scannumber, normalized_signals, movmean_signals, derived_signals, ax, i)

        #ax.plot(first_large_threshold_idx, i ,'m|',markersize=20,markeredgewidth=1)
        #ax.plot(second_smaller_threshold_idx, i ,'m|',markersize=20,markeredgewidth=1)
        #ax.plot(third_sign_change_idx, i ,'r|',markersize=20,markeredgewidth=1)    

    # Similarly for the markers
    #ax.plot([float('nan')], [float('nan')], 'm|', markersize=3, markeredgewidth=1, label='First/Second Threshold')
    #ax.plot([float('nan')], [float('nan')], 'r|', markersize=3, markeredgewidth=1, label='Guessed Signal Start')   

    # decrease the legend size
    ax.legend(loc='best', fontsize=6) 
    pts = plt.ginput(-1,timeout=600,show_clicks=True,mouse_add=MouseButton.RIGHT,mouse_pop=MouseButton.MIDDLE,mouse_stop=None)

    if len(pts) > 0:
        for (x, y) in pts:
            y = round(y)
            y = np.clip(y, 0, 7)
            if x < pre_trigger:
                # ignore signal
                ax.plot(scannumber, normalized_signals[y] + y, color='red', linewidth=1, marker=',', linestyle='-')
                signal_run_times[int(y)] = np.nan
            else:
                ax.plot(x, y, 'k|', markersize=20, markeredgewidth=1)
                signal_run_times[int(y)] = 1000 * (x - pre_trigger) / scan_rate

    plt.close(fig)

    fig, ax = time_signals_plot_init('Timeseries of the Acustic Signals', pre_trigger)

    for i in range(len(names)):
        plot_single_signal(cmap(i), signal_run_times, scannumber, normalized_signals, movmean_signals, derived_signals, ax, i)
        if signal_run_times[i] > 0: 
            ax.plot(signal_run_times[i]/1000*scan_rate + pre_trigger, i, 'k|', markersize=20, markeredgewidth=1)  

    # Similarly for the markers
    ax.plot([float('nan')], [float('nan')], 'k|', markersize=3, markeredgewidth=1, label='Signal Start')
    ax.legend(loc='upper left', fontsize=8)
    plt.savefig(path / f'{filename}.pdf', dpi=300)
    plt.close(fig)
    print(f'{filename}.pdf plotted')

    return signal_run_times 

def delete_pdfs_in_folder(folder_path: Path) -> None:
    """
    Delete all PDF files in the given folder.
    """
    for file_path in folder_path.glob("*.pdf"):
        try:
            file_path.unlink()
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def main(path: Path) -> None:
    """
    Main function to process CSV files, generate plots, and export data.
    """
    delete_pdfs_in_folder(path)
    export_txt_path = path / "export.txt"
    if export_txt_path.exists():

        export_txt_path.unlink()

    config = np.loadtxt(str(path / "config.txt"), dtype=str)
    signal_run_times = []

    for file in path.glob('*.csv'):
        data, header = load_csv(file)
        t = plotter(data, header, path, file.stem)
        signal_run_times.append(t)

    tmean = np.zeros(8)
    probe_locations = config[1:, 1].astype(float)
    signal_run_times = np.array(signal_run_times)

    if np.any(signal_run_times<0):
        signal_run_times[signal_run_times<0] = np.nan
        print("There have been runtimes lower than 0s. They are ignored for the analysis.")

    # Calculate the mean and standard deviation of signal_run_times
    mean_data = np.nanmean(signal_run_times, axis=0)
    std_data = np.nanstd(signal_run_times, axis=0)

    # Calculate z-scores for each entry in signal_run_times
    z_scores = np.abs((signal_run_times - mean_data) / std_data)

    # Apply z-score filtering with a threshold of 1
    z_threshold = 2
    filter_mask = z_scores <= z_threshold

    # Create deep copies of signal_run_times (python works with references by default)
    filtered_signal_times = copy.deepcopy(signal_run_times)
    non_filtered_signal_times = copy.deepcopy(signal_run_times)

    # Apply the filters
    filtered_signal_times[~filter_mask] = np.nan
    non_filtered_signal_times[filter_mask] = np.nan

    # Calculate mean and standard deviation of the filtered data
    tmean = np.nanmean(filtered_signal_times, axis=0)
    sigma_t = np.nanstd(filtered_signal_times, axis=0)

    # Print results
    print('tmean :', np.round(tmean, 1))
    print('sigma_t :', np.round(sigma_t, 1))

    # Plot filtered measurements with crosses
    plt.plot(probe_locations, filtered_signal_times.T, 'bx')
    plt.plot(probe_locations, non_filtered_signal_times.T, 'rx')
    plt.plot([float('nan')], [float('nan')], 'bx', label='Messungen')
    plt.plot([float('nan')], [float('nan')], 'rx', label='Ignorierte Outlier')

    # Plotting the mean with error bars
    plt.errorbar(x=probe_locations, y=tmean, yerr=sigma_t, fmt='kx', ecolor='k', capsize=5)
    plt.xlabel('Position / m')
    plt.ylabel('Time / ms')
    plt.grid() 
    plt.plot([float(config[0,1])],[0.5],'rv',markersize=10, label="Schlagpunkt")
    plt.legend(loc='upper left', fontsize=8)
    plt.waitforbuttonpress(timeout=-1)
    plt.savefig(path / 'Laufzeit.pdf', dpi=300)

    # Save the signal run times data
    np.savetxt(path / 'export.txt', signal_run_times.T, fmt='%10.5f', delimiter=',')

# run via your console using:

# python plotter.py m12
# adapt 'm12' to your folder name you currently use
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV data and plot results.")
    parser.add_argument('path', type=str, help='Path to the directory containing the CSV files')
    args = parser.parse_args()
    main(Path(args.path))
    
# if you run it via spyder or similar, comment the above if bloc and uncomment the line below
# main(Path("m12"))