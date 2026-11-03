from decouple import config
import os
import logging
import subprocess

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

VENV = config("VENV")
logger.info(f"VENV: {VENV}")

REQUIREMENTS_FILE = config("REQUIREMENTS_FILE")
logger.info(f"REQUIREMENTS_FILE: {REQUIREMENTS_FILE}")

TARGET_BRANCH = config("TARGET_BRANCH")
logger.info(f"TARGET_BRANCH: {TARGET_BRANCH}")

UPDATE_DIRECTORIES_FILE = config("UPDATE_DIRECTORIES_FILE")
logger.info(f"UPDATE_DIRECTORIES_FILE: {UPDATE_DIRECTORIES_FILE}")

with open(UPDATE_DIRECTORIES_FILE, "r") as f:
    UPDATE_DIRECTORIES = [
        line
        for line in f.read().splitlines()
        if not line.startswith("#") and line.strip() != ""
    ]
logger.info(f"UPDATE_DIRECTORIES: {UPDATE_DIRECTORIES}")

RUN_GIT_PULL = config("RUN_GIT_PULL", cast=bool, default=True)


def main():
    for directory in UPDATE_DIRECTORIES:
        requirements_file = f"{directory}/{REQUIREMENTS_FILE}"
        if not os.path.exists(requirements_file):
            logger.warning(f"Requirements file not found at: {requirements_file}")
            continue

        logger.info(f"Run git pull on: {directory}")
        subprocess.run(["git", "-C", directory, "checkout", TARGET_BRANCH])

        if RUN_GIT_PULL:
            subprocess.run(["git", "-C", directory, "pull"])

        venv_path = f"{directory}/{VENV}"
        logger.info(f"Removing old virtual environment at: {venv_path}")
        subprocess.run(["rm", "-rf", venv_path])

        logger.info(f"Creating new virtual environment at: {venv_path}")
        subprocess.run(["python3.15", "-m", "venv", venv_path])

        logger.info(f"Installing dependencies from: {requirements_file}")
        subprocess.run([f"{venv_path}/bin/pip", "install", "--upgrade", "pip"])

        logger.info(f"Upgrading pip in virtual environment at: {venv_path}")
        subprocess.run(
            [
                f"{venv_path}/bin/pip",
                "install",
                "-r",
                requirements_file,
                "--no-cache-dir",
            ]
        )

        logger.info(f"Freezing installed dependencies to: {directory}/requirements.txt")
        result = subprocess.run(
            [f"{venv_path}/bin/pip", "freeze"],
            check=True,
            capture_output=True,
            text=True,
        )
        with open(f"{directory}/requirements.txt", "w") as f:
            f.write(result.stdout)

        # check if requirements.txt has changed and commit if necessary
        subprocess.run(["git", "-C", directory, "add", "requirements.txt"])
        if (
            subprocess.run(
                ["git", "-C", directory, "diff", "--cached", "--quiet"]
            ).returncode
            != 0
        ):
            logger.info(f"Committing updated requirements.txt in: {directory}")
            subprocess.run(
                ["git", "-C", directory, "commit", "-m", "Update requirements.txt"]
            )
            subprocess.run(["git", "-C", directory, "push"])


if __name__ == "__main__":
    main()
