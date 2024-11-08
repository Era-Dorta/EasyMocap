#!/usr/bin/env python3
import os
import subprocess
import time
from pathlib import Path
import argparse

EASYMOCAP_IMAGE="/tudelft.net/staff-umbrella/CaptureLab/Apptainer/easymocap-0.2.3.sif"
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


def submit_processing_jobs(recording_number: str, account: str, partition: str, verbose: bool = False, dep_job_ids: None |  list[int] = None
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

    if dep_job_ids is not None:
        job_deps_str = ":".join(map(str, dep_job_ids))
        cmd += ["--dependency", f"afterok:{job_deps_str}"]

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--dep-job-ids', nargs="*", type=int, help='Depdency job ids.')
    parser.add_argument('--account', default="ewi-insy-prb", help='Account.')
    parser.add_argument('--recording_number', default="154_short", help='The recording number.')
    parser.add_argument('--partition', default="insy,general", help='Partition to use.')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    os.chdir(Path(__file__).parent)

    add_clean_up_job = False

    job_ids = list(submit_processing_jobs(
        recording_number=args.recording_number,
        account=args.account,
        partition=args.partition,
        verbose=args.verbose,
        dep_job_ids=args.dep_job_ids
    ))

    if add_clean_up_job:
        job_ids.append(submit_clean_up_job(args.recording_number, job_ids, verbose=args.verbose))

    print(f"\nIf you made a mistake, you can cancel the jobs with\nscancel {' '.join(map(str, job_ids))}")
