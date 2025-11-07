#!/usr/bin/env python3
"""
dev_start.py

One-command helper to:
 - build the Docker image(s) via docker-compose (or docker compose)
 - start the stack detached
 - wait for the app health endpoint to report "ready"
 - open the UI in your default browser (http://localhost:8000/static/index.html)

Usage:
  python dev_start.py            # default behaviour
  python dev_start.py --no-browser
  python dev_start.py --timeout 240
  python dev_start.py --compose-file my-compose.yml
  python dev_start.py --url http://localhost:8000/healthz

Requirements:
 - Docker Desktop running and available on PATH
 - docker-compose (or the newer `docker compose` command) available
 - docker-compose.yml present in repo root (or provide --compose-file)
 - Python 3.7+
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
import webbrowser
from typing import Optional

DEFAULT_HEALTH = "http://localhost:8000/healthz"
DEFAULT_UI = "http://localhost:8000/static/index.html"

def find_compose_cmd() -> Optional[list[str]]:
    """
    Return a command list prefix for compose: try `docker-compose`, then `docker compose`.
    Returns None if none found.
    """
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    # newer Docker uses 'docker compose' as subcommand
    if shutil.which("docker"):
        # test whether 'docker compose' works (some docker installs may not have it)
        try:
            subprocess.run(["docker", "compose", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return ["docker", "compose"]
        except Exception:
            pass
    return None

def run_cmd(cmd: list[str], check: bool = True) -> int:
    "Run a shell command, print it, return exit code (raises on non-zero if check=True)."
    print("+", " ".join(cmd))
    res = subprocess.run(cmd)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed (exit {res.returncode}): {' '.join(cmd)}")
    return res.returncode

def wait_for_health(url: str, timeout: int = 120, poll_interval: float = 2.0) -> bool:
    """
    Poll the health endpoint until it reports ready or timeout expires.
    Returns True if ready, False if timeout.
    Accepts JSON with {"status": "ready"} or plain 200 OK as success.
    """
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                code = resp.getcode()
                content = resp.read().decode("utf-8", errors="ignore").strip()
                if code == 200:
                    # try parse JSON if available
                    try:
                        j = json.loads(content) if content else {}
                        st = j.get("status") or j.get("status", "")
                        if isinstance(st, str) and st.lower() == "ready":
                            print(f"[health] ready (via JSON) on attempt {attempt}")
                            return True
                        # some setups return {"status":"starting"} until ready; continue polling
                        # fallback: if 200 and no JSON, treat as ready
                        if not content:
                            print(f"[health] received 200 empty body -> treat as ready (attempt {attempt})")
                            return True
                    except Exception:
                        # not JSON — treat HTTP 200 as success
                        print(f"[health] HTTP 200 (non-JSON) -> treat as ready (attempt {attempt})")
                        return True
                else:
                    print(f"[health] HTTP {code} (attempt {attempt})")
        except urllib.error.HTTPError as e:
            print(f"[health] HTTPError {e.code} (attempt {attempt})")
        except urllib.error.URLError as e:
            print(f"[health] URLError ({e}) (attempt {attempt})")
        except Exception as e:
            print(f"[health] Exception ({e}) (attempt {attempt})")

        time.sleep(poll_interval)
        # progressive backoff up to 5s
        poll_interval = min(poll_interval * 1.1, 5.0)

    print(f"[health] timeout after {timeout} seconds waiting for {url}")
    return False

def main():
    ap = argparse.ArgumentParser(description="Build, start docker-compose, wait for app, open browser.")
    ap.add_argument("--no-browser", action="store_true", help="Don't open the browser automatically")
    ap.add_argument("--timeout", type=int, default=180, help="Seconds to wait for /healthz (default 180)")
    ap.add_argument("--compose-file", type=str, default="docker-compose.yml", help="Path to docker-compose file")
    ap.add_argument("--url", type=str, default=DEFAULT_HEALTH, help="Health endpoint to poll")
    ap.add_argument("--ui-url", type=str, default=DEFAULT_UI, help="UI URL to open in browser")
    ap.add_argument("--skip-down", action="store_true", help="Skip running 'compose down' before starting")
    args = ap.parse_args()

    # sanity checks
    if not os.path.exists(args.compose_file):
        print(f"Error: compose file not found at {args.compose_file}", file=sys.stderr)
        sys.exit(2)

    compose_cmd_prefix = find_compose_cmd()
    if compose_cmd_prefix is None:
        print("Error: neither `docker-compose` nor `docker compose` was found on PATH.", file=sys.stderr)
        sys.exit(2)

    # Use the detected compose command and pass -f file if not default
    # Example: ['docker-compose', '-f', 'docker-compose.yml', 'up', '--build', '-d']
    compose_base = compose_cmd_prefix.copy()
    # if user specified specific compose filename, include -f flag
    if args.compose_file and os.path.basename(args.compose_file) != "docker-compose.yml":
        compose_base += ["-f", args.compose_file]

    try:
        if not args.skip_down:
            print("Bringing any previous stack down (if present)...")
            run_cmd(compose_base + ["down"], check=False)

        print("Starting compose stack (build + detached)... This may take a few minutes for first build.")
        run_cmd(compose_base + ["up", "--build", "-d"])

        print(f"Polling health endpoint: {args.url} (timeout {args.timeout}s)...")
        ready = wait_for_health(args.url, timeout=args.timeout)
        if not ready:
            print("App did not become ready in time. Showing recent logs (last 200 lines):")
            try:
                run_cmd(compose_base + ["logs", "--tail", "200"])
            except Exception as e:
                print("Failed to fetch logs:", e)
            print("Exiting with failure.")
            sys.exit(3)

        print("App is ready.")
        if not args.no_browser:
            print(f"Opening UI: {args.ui_url}")
            webbrowser.open(args.ui_url)
        else:
            print("Skipping browser open (per --no-browser).")

        print("Finished successfully. Use Ctrl-C or `docker-compose down` to stop the stack when done.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
        sys.exit(1)
    except Exception as exc:
        print("Error:", exc, file=sys.stderr)
        try:
            print("Printing recent logs to assist debugging:")
            run_cmd(compose_base + ["logs", "--tail", "200"], check=False)
        except Exception:
            pass
        sys.exit(4)

if __name__ == "__main__":
    main()