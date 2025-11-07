# File: docker_helper.py
import subprocess
import os
import argparse

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

def build(image_name="hospitrack:latest"):
    run(["docker", "build", "-t", image_name, "."])

def run_container(image_name="hospitrack:latest", data_dir="./data", ports=None, extra_args=None):
    if ports is None:
        ports = {"8000": "8000", "5678": "5678"}
    abs_data = os.path.abspath(data_dir)
    cmd = [
        "docker", "run", "--rm", "-it",
        "-v", f"{abs_data}:/app/data:ro"
    ]
    for host_p, cont_p in ports.items():
        cmd += ["-p", f"{host_p}:{cont_p}"]
    if extra_args:
        cmd += extra_args
    cmd += [image_name]
    run(cmd)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--build", action="store_true", help="Build the Docker image")
    p.add_argument("--run", action="store_true", help="Run the Docker container (after build)")
    p.add_argument("--image", default="hospitrack:latest", help="Image name")
    p.add_argument("--data", default="./data", help="Local data directory to mount into container")
    args = p.parse_args()

    if args.build:
        build(args.image)
    if args.run:
        run_container(args.image, data_dir=args.data)

if __name__ == "__main__":
    main()