import subprocess
import json
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
import requests
from urllib.parse import urlparse, urljoin

# ==========================================================
# CONFIG: FFmpeg and FFprobe absolute paths
# ==========================================================
ffmpeg_path = r"C:\Users\Priyanshu.verma\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\Priyanshu.verma\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin\ffprobe.exe"


# ==========================================================
# UTILITY: Run FFprobe command safely
# ==========================================================
def run_ffprobe(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"❌ FFprobe error:\n{result.stderr}")
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse ffprobe output.")
        return {}


# ==========================================================
# FUNCTION 1: Extract metadata via FFprobe
# ==========================================================
def get_media_info(file_path):
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries",
        "format=duration,bit_rate,format_name:stream=index,codec_name,codec_type,"
        "sample_rate,channels,bits_per_raw_sample,profile,tags=creation_time",
        "-of", "json",
        file_path
    ]
    info = run_ffprobe(cmd)
    if not info:
        return {}

    audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    audio_info = audio_streams[0] if audio_streams else {}

    sample_rate = audio_info.get("sample_rate")
    sample_rate_str = f"{int(sample_rate)/1000:.1f} kHz" if sample_rate else "N/A"

    return {
        "format": info.get("format", {}).get("format_name", "N/A"),
        "duration_sec": round(float(info.get("format", {}).get("duration", 0)), 2),
        "bitrate_kbps": round(int(info.get("format", {}).get("bit_rate", 0)) / 1000, 2)
            if info.get("format", {}).get("bit_rate") else "N/A",
        "audio": {
            "codec": audio_info.get("codec_name", "N/A"),
            "profile": audio_info.get("profile", "N/A"),
            "channels": audio_info.get("channels", "N/A"),
            "sample_rate": sample_rate_str,
            "bits_per_sample": audio_info.get("bits_per_raw_sample", "N/A"),
        }
    }


# ==========================================================
# FUNCTION 2: Parse master playlist and find audio-only variant
# ==========================================================
def get_audio_variant_from_master(master_url):
    print("\n🎯 Scanning master playlist for audio variants...")
    try:
        response = requests.get(master_url)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch master playlist: {e}")
        return None

    text = response.text
    import re
    variants = re.findall(r'URI="([^"]+-audio-[^"]+\.m3u8)"', text)
    if not variants:
        variants = [line.strip() for line in text.splitlines()
                    if "-audio-" in line and line.strip().endswith(".m3u8")]
    if not variants:
        print("❌ No audio variants found in master playlist.")
        return None

    preferred = None
    for v in variants:
        if "576" in v:
            preferred = v
            break
    if not preferred:
        preferred = variants[-1]

    selected_variant = urljoin(master_url, preferred)
    print(f"✅ Selected audio variant: {selected_variant}\n")
    return selected_variant


# ==========================================================
# FUNCTION 3: Decode CMAF/HLS audio variant → WAV
# ==========================================================
def decode_m3u8_to_wav(m3u8_path, decoded_wav):
    print("🎬 Running FFmpeg decode (CMAF-aware)...")
    cmd = [
        ffmpeg_path,
        "-protocol_whitelist", "file,http,https,tcp,tls",
        "-allowed_extensions", "ALL",
        "-i", m3u8_path,
        "-vn",
        "-c:a", "pcm_s24le",
        "-ar", "96000",
        "-ac", "2",
        decoded_wav
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg Error:\n{result.stderr}")
        return False
    print(f"✅ Decoded WAV saved at: {decoded_wav}")
    return True


# ==========================================================
# FUNCTION 4: Compare metadata info (side-by-side)
# ==========================================================
def compare_metadata(original, decoded):
    print("\n📊 Metadata Comparison\n" + "=" * 40)
    print("🎧 Original File:")
    print(json.dumps(original, indent=2))
    print("\n🎧 Decoded File:")
    print(json.dumps(decoded, indent=2))


# ==========================================================
# ✅ FUNCTION 5: Full waveform comparison (entire file)
# ==========================================================
def compare_waveforms(file1, file2):
    """Compare entire waveform (not just first 200 ms)."""
    print("\n🔍 Performing FULL waveform similarity analysis...")
    y1, sr1 = librosa.load(file1, sr=None, mono=True)
    y2, sr2 = librosa.load(file2, sr=sr1, mono=True)

    min_len = min(len(y1), len(y2))
    y1, y2 = y1[:min_len], y2[:min_len]

    diff = y1 - y2
    rms_error = np.sqrt(np.mean(diff ** 2))
    corr = np.corrcoef(y1, y2)[0, 1]

    print(f"\n🎧 Waveform Analysis Results:")
    print(f"📏 RMS Error: {rms_error:.6f}")
    print(f"🔗 Correlation: {corr:.6f}")

    if corr > 0.99:
        print("✅ Very close match (almost identical to human ear)")
    elif corr > 0.95:
        print("⚠️ Small audible difference possible")
    else:
        print("❌ Significant difference (compression artifacts likely)")

    return y1, y2, sr1


# ==========================================================
# ✅ FUNCTION 6: Plot entire waveform instead of 200 ms
# ==========================================================
def plot_waveform_full(y1, y2, sr):
    duration_sec = len(y1) / sr
    plt.figure(figsize=(14, 4))
    plt.plot(y1, label='Original WAV', alpha=0.7)
    plt.plot(y2, label='Decoded (CMAF)', alpha=0.7)
    plt.title(f"Full Waveform Comparison — {duration_sec:.2f} sec analyzed")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ==========================================================
# FUNCTION 7: Frequency spectrum difference
# ==========================================================
def plot_spectrum_diff(y1, y2, sr):
    print("\n📈 Generating frequency response plot...")
    fft_len = 8192
    orig_fft = np.abs(np.fft.rfft(y1[:fft_len]))
    dec_fft = np.abs(np.fft.rfft(y2[:fft_len]))
    freqs = np.fft.rfftfreq(fft_len, 1 / sr)

    plt.figure(figsize=(10, 5))
    plt.semilogx(freqs, 20 * np.log10(orig_fft + 1e-9), label="Original WAV")
    plt.semilogx(freqs, 20 * np.log10(dec_fft + 1e-9), label="Decoded CMAF/AAC")
    plt.title("Frequency Spectrum Comparison (First 8192 samples)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (dB)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ==========================================================
# MAIN EXECUTION
# ==========================================================
if __name__ == "__main__":
    original_wav = r"C:\Users\Priyanshu.verma\Videos\nSepia Content\Music\Bhramaand.wav"
    master_m3u8 = "https://d3rktbievijp3p.cloudfront.net/content/84/cmaf_abr_bundle/bhramaand_1762236624.m3u8?Expires=1762240765&Signature=Fa3P3kMH7QdvobyC7WOGWr9IXYFUdXwih0CT-7sv3OPdg8zbqFg~mNdTp8Ok3LlQ629Cc2a5neuRXeJfm2mmlz3iLsr0gf7HDcOUwJn0p3hBJ8faTuU7dt-Ce0KNDinfDKmKiQotEYmLqTT5tz5tXDs8gBAvhUx1aF-rtMV5vnaAA62U7vrf68Xp7K5e7KcSZJvqORfXoEXiGg6cW-ZmiZhjTpzFdXrGEA5Q2hzKDHmQq6~u7tRLwcI5dJhMYkDTuH5IiWjZMInaQpHaq6trQoV5L~1AaT~1PuFzc3aHNCiox~l3sM7CBPR20Yamfa4FjXNgT6qI4VBW4qlO4mBHxw__&Key-Pair-Id=K35YCGEH6LAKFE"
    output_dir = os.path.join(os.getcwd(), "converted_files")
    os.makedirs(output_dir, exist_ok=True)
    decoded_wav = os.path.join(output_dir, os.path.basename(original_wav))

    audio_variant = get_audio_variant_from_master(master_m3u8)
    if not audio_variant:
        print("❌ No valid audio variant found. Exiting.")
        exit()

    ok = decode_m3u8_to_wav(audio_variant, decoded_wav)
    if not ok:
        raise SystemExit("❌ Decoding failed, aborting comparison.")

    orig_info = get_media_info(original_wav)
    dec_info = get_media_info(decoded_wav)
    compare_metadata(orig_info, dec_info)
    
    y1, y2, sr = compare_waveforms(original_wav, decoded_wav)
    duration_limit_sec = 30
    samples = int(duration_limit_sec * sr)
    # pick middle 30 seconds
    mid_start = max(0, (len(y1) // 2) - (samples // 2))
    mid_end = mid_start + samples

    plot_waveform_full(y1[mid_start:mid_end], y2[mid_start:mid_end], sr)
    plot_spectrum_diff(y1[mid_start:mid_end], y2[mid_start:mid_end], sr)

    print("\n✅ Done — full waveform comparison complete.")
