import os
from os.path import join
import subprocess
from pathlib import Path

def load_subs(path, subs):
    if len(subs) == 0:
        subs = sorted(os.listdir(join(path, 'videos_mp4')))
    subs = [sub for sub in subs if os.path.isdir(join(path, 'videos_mp4', sub))]
    if len(subs) == 0:
        subs = ['']
    return subs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, default=None, help="the path of data")
    parser.add_argument('--camera_to_process', type=str)
    args = parser.parse_args()

    if args.camera_to_process == "":
        args.camera_to_process = None

    processed_mp4_folder = Path(args.path) / 'videos_mp4'
    processed_mp4_folder.mkdir(exist_ok=True)

    data_path = Path(args.path) / 'videos'
    
    print("Processing videos")
    for input_video_mp4 in data_path.iterdir():
        if args.camera_to_process is not None and input_video_mp4.stem != args.camera_to_process:
            print(f"Skip {input_video_mp4.name}")
            continue

        output_video_avi = data_path / (input_video_mp4.stem + ".avi")

        cmd = ["ffmpeg", "-i", input_video_mp4, "-c:v", "copy", "-c:a", "copy", output_video_avi]
        print(" ".join(map(str, cmd)))
        subprocess.run(cmd)

        input_video_mp4.rename(processed_mp4_folder / input_video_mp4.name)

    print("Done")
