import os
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

def detect_drum_onsets(
    input_file,
    log_file="beat_detection",
    frame_ms=10,
    hop_ms=5,
    window_ms=1000,
    threshold_dbfs=-13.0,
    relative_threshold_db=6.0,
    noise_gate_dbfs=-45.0,
    min_hit_interval_ms=100,
    peak_neighborhood_ms=60,
    plot=True,
):

    print("Loading audio...")
    audio = AudioSegment.from_file(input_file)
    samples = np.asarray(audio.get_array_of_samples(), dtype=np.float32)

    if audio.channels > 1:
        samples = samples.reshape(-1, audio.channels).mean(axis=1)

    samples /= float(audio.max_possible_amplitude)
    sr = audio.frame_rate

    frame_n = max(1, int(sr * frame_ms / 1000))
    hop_n = max(1, int(sr * hop_ms / 1000))
    window_frames = max(3, int(window_ms / hop_ms))
    if window_frames % 2 == 0:
        window_frames += 1

    print("Calculating short-time RMS...")
    rms = []
    times = []

    for start in range(0, max(1, len(samples) - frame_n + 1), hop_n):
        frame = samples[start:start + frame_n]
        if len(frame) == 0:
            continue
        rms.append(np.sqrt(np.mean(frame * frame)))
        times.append(start / sr * 1000)

    rms = np.asarray(rms)
    times = np.asarray(times)

    eps = 1e-10
    energy_db = 20 * np.log10(np.maximum(rms, eps))

    # Local mean-square energy, computed efficiently with cumulative sums.
    energy = rms * rms
    # Use only previous audio to calculate the local average.
    window_frames = max(1, int(window_ms / hop_ms))

    prefix = np.concatenate(([0.0], np.cumsum(energy)))

    indices = np.arange(len(energy))

    left = np.maximum(0, indices - window_frames)
    right = indices

    local_energy = (
        prefix[right] - prefix[left]
    ) / np.maximum(1, right - left)

    # Convert to dBFS.
    local_db = 10 * np.log10(np.maximum(local_energy, eps))

    # A local threshold, capped by the absolute threshold ceiling.
    adaptive_db = np.minimum(
        threshold_dbfs,
        local_db + relative_threshold_db
    )

    # Detect increases in energy relative to the previous frame.
    novelty = np.maximum(0.0, energy_db - np.roll(energy_db, 1))
    novelty[0] = 0.0

    # Less smoothing preserves short drum attacks.
    smooth_n = 2
    kernel = np.ones(smooth_n) / smooth_n

    # Candidate frames must be loud enough and exceed adaptive threshold.
    eligible = (
        (energy_db >= adaptive_db) &
        (local_db >= noise_gate_dbfs)
    )

    # Smooth the RMS envelope slightly to remove tiny fluctuations.
    smooth_kernel = np.ones(3) / 3.0
    peak_signal = np.convolve(rms, smooth_kernel, mode="same")

    peak_db = 20 * np.log10(np.maximum(peak_signal, eps))

    # Find actual local loudness peaks, not rising-edge peaks.
    neighborhood = max(1, int(peak_neighborhood_ms / hop_ms))

    candidates = []

    for i in range(1, len(peak_db) - 1):
        if not eligible[i]:
            continue

        # Must be a local maximum.
        if peak_db[i] < peak_db[i - 1]:
            continue

        if peak_db[i] <= peak_db[i + 1]:
            continue

        # Must be the dominant peak in its neighborhood.
        lo = max(0, i - neighborhood)
        hi = min(len(peak_db), i + neighborhood + 1)

        if peak_db[i] >= np.max(peak_db[lo:hi]):
            candidates.append(i)


    # Non-maximum suppression:
    # If several peaks are close, keep only the loudest one.
    min_distance = max(1, int(min_hit_interval_ms / hop_ms))

    selected = []

    for i in sorted(candidates, key=lambda x: peak_db[x], reverse=True):
        if all(abs(i - j) >= min_distance for j in selected):
            selected.append(i)

    selected.sort()

    hit_times = times[selected]

    # Save timestamps and diagnostics.
    txt_path = log_file + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("# Drum onset timestamps (milliseconds)\n")
        f.write(f"# Frame: {frame_ms} ms, hop: {hop_ms} ms\n")
        f.write(f"# Adaptive window: {window_ms} ms\n")
        f.write(f"# Threshold ceiling: {threshold_dbfs} dBFS\n")
        f.write(f"# Relative threshold: +{relative_threshold_db} dB\n")
        f.write(f"# Noise gate: {noise_gate_dbfs} dBFS\n")
        f.write(f"# Minimum hit interval: {min_hit_interval_ms} ms\n\n")
        for t in hit_times:
            f.write(f"{t:.2f}\n")

    print(f"Detected {len(hit_times)} possible hits.")
    print(f"Saved timestamps to {txt_path}")

    if plot:
        print("Generating diagnostic plot...")
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.plot(times / 1000, energy_db, label="RMS level (dBFS)", linewidth=0.8)
        ax.plot(times / 1000, adaptive_db, label="Adaptive threshold", linewidth=1.0)
        ax.plot(times / 1000, local_db, label="Local average", alpha=0.65, linewidth=0.8)
        ax.axhline(noise_gate_dbfs, linestyle="--", label="Noise gate")
        if len(hit_times):
            ax.scatter(hit_times / 1000, energy_db[selected],
                       marker="x", s=35, label="Detected hits")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Level (dBFS)")
        ax.set_title("Adaptive Drum Onset Detection")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        plot_path = log_file + "_plot.png"
        fig.savefig(plot_path, dpi=150)
        plt.show()
        print(f"Saved plot to {plot_path}")

    return hit_times


# ---------------- CONFIGURATION ----------------

INPUT_FLAC = r"D:\Python\GAME\assets\musics\separated\htdemucs\bad_apple\drums.flac"
LOG_TXT = r"..\temp\loudness_log"

detect_drum_onsets(
    INPUT_FLAC,
    log_file=LOG_TXT,
    frame_ms=20,
    hop_ms=5,
    window_ms=1500,
    threshold_dbfs=-12,
    relative_threshold_db=4.0,
    noise_gate_dbfs=-27.0,
    min_hit_interval_ms=85,
    peak_neighborhood_ms=60,
    plot=True,
)