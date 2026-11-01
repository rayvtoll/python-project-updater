# Python project updater

## Why this project
I would like to update every project on a weekly to eventually daily basis. Let's automate this process!

## How to setup
1. Create a file `update_directories.txt` containing a list (per row) of all directories containing python projects that you wish to update.
2. Create a file `.env` containing the following rows:    
    ```
    TARGET_BRANCH=main
    VENV=.venv
    UPDATE_DIRECTORIES_FILE=update_directories.txt
    REQUIREMENTS_FILE=dev-requirements.txt
    ```

## How to run
```
# first run
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt --no-cache-dir

# every run
.venv/bin/python .
```