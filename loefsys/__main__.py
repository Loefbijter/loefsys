"""Entrypoint for Loefsys application."""

import argparse
import subprocess


def server():
    """Start the gunicorn server process."""
    subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=False)
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=False)
    subprocess.run(
        ["gunicorn", "-b", ":80", "-w", "3", "loefsys.wsgi:application"], check=False
    )


def worker():
    """Start the Celery worker process."""
    subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=False)
    subprocess.run(["celery", "-A", "loefsys", "worker", "-B"], check=False)


actions = {"server": server, "worker": worker}

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Loefsys")
    parser.add_argument("action", choices=actions.keys())
    args = parser.parse_args()
    actions[args.action]()
