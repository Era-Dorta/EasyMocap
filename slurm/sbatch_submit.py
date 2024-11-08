#!/usr/bin/env python3
import os
import subprocess
import time
from pathlib import Path

EASYMOCAP_IMAGE="/tudelft.net/staff-umbrella/CaptureLab/Apptainer/easymocap-0.2.2.sif"
OPENPOSE_IMAGE="/tudelft.net/staff-umbrella/CaptureLab/Apptainer/openpose-1.7.0.sif"
DATA_DIRECTORY="/tudelft.net/staff-umbrella/CaptureLab/Recordings"

# The data directory inside the container
CONTAINER_DATA_DIRECTORY="/home/user/easymocap/EasyMocap/data/examples/_data"

def get_job_environ(recording_number: str) -> dict[str, str]:
    env = dict(
        os.environ,
        RECORDING_NUMBER=recording_number,
        EASYMOCAP_IMAGE=EASYMOCAP_IMAGE,
        OPENPOSE_IMAGE=OPENPOSE_IMAGE,
        DATA_DIRECTORY=DATA_DIRECTORY,
        CONTAINER_DATA_DIRECTORY=CONTAINER_DATA_DIRECTORY,
    )
    return env


def submit_processing_jobs(recording_number: str, account: str, partition: str, verbose: bool = False
) -> tuple[int, int]:
    new_env = get_job_environ(recording_number)
    name_identifier = f"{recording_number}"
    print(name_identifier)

    # fmt: off
    cmd = [
        "sbatch",
        "--job-name", f"get-2d-keypoints-{name_identifier}",
        "--account", account,
        "--partition", partition,
        "submit_extract_2d_keypoints.sh",
    ]
    # fmt: on

    if verbose:
        print(" ".join(cmd))

    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env)

    time.sleep(0.1)  # Wait a bit to ensure slurm doesn't crash from submitting jobs too fast

    if ret.returncode != 0:
        raise RuntimeError(ret.stdout + ret.stderr)

    stdout = ret.stdout.decode("utf-8")
    if not stdout.startswith("Submitted batch job"):
        raise RuntimeError(ret.stdout + ret.stderr)

    print(stdout.strip())
    job_id = int(stdout.replace("Submitted batch job ", ""))

    # fmt: off
    cmd = [
        "sbatch",
        "--job-name", f"2d-keypoints-to-3d-{name_identifier}",
        "--account", account,
        "--partition", partition,
        "--dependency", f"afterok:{job_id}",
        "submit_lift_2d_keypoints_to_3d.sh",
    ]
    # fmt: on

    if verbose:
        print(" ".join(cmd))

    ret = subprocess.run(cmd, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.1)

    stdout = ret.stdout.decode("utf-8")
    print(stdout.strip() + "\n")
    return job_id, int(stdout.replace("Submitted batch job ", ""))


def submit_clean_up_job(recording_number: str, job_dependencies: list[int], verbose: bool = False):
    """Submit a job that will delete the directory with the png files."""
    new_env = get_job_environ(None, recording_number)

    print(f"Clean up for {recording_number}")
    job_deps_str = ":".join(map(str, job_dependencies))

    # fmt: off
    cmd = [
            "sbatch",
            "--job-name", f"cleanup-{recording_number}",
            "--account", account,
            "--partition", partition,
            "--dependency", f"afterok:{job_deps_str}",
            "submit_clean_up.sh",
        ]
    # fmt: on

    if verbose:
        print(" ".join(cmd))

    ret = subprocess.run(cmd, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout = ret.stdout.decode("utf-8")
    print(stdout.strip() + "\n")

    return int(stdout.replace("Submitted batch job ", ""))

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)

    account = "ewi-insy-prb"
    partition = "insy,general"
    recording_number = "154_short"
    verbose = False
    add_clean_up_job = False

    job_ids = list(submit_processing_jobs(
        recording_number=recording_number,
        account=account,
        partition=partition,
        verbose=verbose,
    ))

    if add_clean_up_job:
        job_ids.append(submit_clean_up_job(recording_number, job_ids, verbose=verbose))

    print(f"\nIf you made a mistake, you can cancel the jobs with\nscancel {' '.join(map(str, job_ids))}")
