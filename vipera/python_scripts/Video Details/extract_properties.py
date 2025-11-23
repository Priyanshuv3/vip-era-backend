import subprocess
import json
import os

def get_media_info(file_path):
    ffprobe_path = r"C:\Users\Priyanshu.verma\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin\ffprobe.exe"

    if not os.path.exists(ffprobe_path):
        raise FileNotFoundError(f"❌ ffprobe not found at: {ffprobe_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found at: {file_path}")

    # ✅ Run ffprobe and get JSON output
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries",
        "format=duration,bit_rate,format_name:stream=index,codec_name,codec_type,width,height,avg_frame_rate,"
        "display_aspect_ratio,pix_fmt,color_space,color_transfer,color_primaries,nb_frames,"
        "sample_rate,channels,channel_layout,bits_per_raw_sample,profile,tags=creation_time",
        "-of", "json",
        file_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"❌ ffprobe error:\n{result.stderr}")

    info = json.loads(result.stdout)

    # ✅ Separate video/audio streams
    video_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]

    video_info = video_streams[0] if video_streams else {}
    audio_info = audio_streams[0] if audio_streams else {}

    # ✅ Process frame rate (e.g., "30000/1001")
    fps = 0
    if "avg_frame_rate" in video_info and video_info["avg_frame_rate"] != "0/0":
        num, den = video_info["avg_frame_rate"].split('/')
        fps = round(float(num) / float(den), 2)

    # ✅ Convert sample rate to readable format
    sample_rate = audio_info.get("sample_rate")
    sample_rate_str = f"{int(sample_rate)/1000:.1f} kHz" if sample_rate else "N/A"

    # ✅ Final structured output
    return {
        "format": info["format"].get("format_name", "N/A"),
        "duration_sec": round(float(info["format"].get("duration", 0)), 2),
        "bitrate_mbps": round(int(info["format"].get("bit_rate", 0)) / 1_000_000, 2),
        "bitrate_kbps": round(int(info["format"].get("bit_rate", 0)) / 1000, 2),

        # 🎥 Video Info
        "video": {
            "resolution": f"{video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}",
            "aspect_ratio": video_info.get("display_aspect_ratio", "N/A"),
            "fps": fps,
            "codec": video_info.get("codec_name", "N/A"),
            "profile": video_info.get("profile", "N/A"),
            "pixel_format": video_info.get("pix_fmt", "N/A"),
            "color_space": video_info.get("color_space", "N/A"),
            "color_primaries": video_info.get("color_primaries", "N/A"),
            "total_frames": video_info.get("nb_frames", "N/A"),
        },

        # 🎧 Audio Info
        "audio": {
            "codec": audio_info.get("codec_name", "N/A"),
            "channels": audio_info.get("channels", "N/A"),
            "channel_layout": audio_info.get("channel_layout", "N/A"),
            "sample_rate": sample_rate_str,
            "bits_per_sample": audio_info.get("bits_per_raw_sample", "N/A"),
            "bitrate_kbps": round(int(audio_info.get("bit_rate", 0)) / 1000, 2)
                if audio_info.get("bit_rate") else "N/A",
        },


        "creation_time": video_info.get("tags", {}).get("creation_time", "N/A"),
    }


# ✅ Example usage
if __name__ == "__main__":
    file_path = input("Enter file path or URL: ").strip()
    file_path = os.path.normpath(file_path)
    details = get_media_info(file_path)

    print(f"\n📄 File: {file_path}")
    print(f"Format: {details['format']}")
    print(f"Duration: {details['duration_sec']} sec")
    print(f"Bitrate: {details['bitrate_kbps']} kbps ({details['bitrate_mbps']} Mbps)")
    print(f"Creation Time: {details['creation_time']}\n")

    print("🎥 Video Info:")
    for key, value in details["video"].items():
        print(f"  {key}: {value}")

    print("🎧 Audio Info:")
    for key, value in details["audio"].items():
        print(f"  {key}: {value}")
