import os
import time
import requests
import json
import base64
import logging
import subprocess  # Import subprocess
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from the .env file
load_dotenv()

# Configuration variables
BITBUCKET_REPO = os.getenv("BITBUCKET_REPO")
BITBUCKET_USER = os.getenv("BITBUCKET_USER")
BITBUCKET_TOKEN = os.getenv("BITBUCKET_TOKEN")
SONAR_SCANNER = os.getenv("SONAR_SCANNER")
SONAR_PROJECT_PROPERTIES = os.getenv("SONAR_PROJECT_PROPERTIES")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL"))
PROJECT_PATH = os.getenv("PROJECT_PATH")

# Function to fetch open PRs from Bitbucket
def fetch_open_prs():
    print("Fetching open PRs...")
    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_REPO}/pullrequests?state=OPEN"
    print(f"URL: {url}")

    # Encode credentials for Basic Authentication
    credentials = f"{BITBUCKET_USER}:{BITBUCKET_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    print(f"Encoded Credentials: {encoded_credentials}")

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
    }
    print(f"Headers: {headers}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx
        prs = response.json()
        with open("prs.json", "w") as file:
            json.dump(prs, file, indent=4)
        print("Fetched PRs and saved to prs.json.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch PRs: {e}")
        if 'response' in locals():
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

# Function to read and parse the SonarQube properties file
def get_sonar_properties(filepath):
    """
    Reads the SonarQube properties file and returns a dictionary of properties.

    Args:
        filepath (str): The path to the sonar-project.properties file.

    Returns:
        dict: A dictionary containing the SonarQube properties.
    """
    properties = {}

    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                # Ignore empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Split the line into key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
    except Exception as e:
        print(f"Error reading SonarQube properties: {e}")

    return properties

# Function to process each PR
def process_prs():
    print("Processing PRs...")
    if not os.path.exists("prs.json"):
        print("prs.json file not found.")
        return

    with open("prs.json", "r") as file:
        prs = json.load(file)

    for pr in prs.get("values", []):
        branch = pr["source"]["branch"]["name"]
        pr_id = pr["id"]
        print(f"Processing PR #{pr_id} on branch {branch}...")

        # Construct the full path of the SonarQube properties file
        sonar_properties_path = os.path.join(PROJECT_PATH, SONAR_PROJECT_PROPERTIES)
        print(f"Checking SonarQube project properties file at: {sonar_properties_path}")

        # Check if the SonarQube properties file exists at the specified path
        if not os.path.exists(sonar_properties_path):
            print(f"SonarQube project properties file '{sonar_properties_path}' not found.")
            return

        try:
            # Checkout the PR branch
            subprocess.run(["git", "fetch", "origin", branch], check=True, cwd=PROJECT_PATH)
            subprocess.run(["git", "checkout", branch], check=True, cwd=PROJECT_PATH)

            # Read SonarQube properties
            sonar_props = get_sonar_properties(sonar_properties_path)
            sonar_args = " ".join([f"-D{key}={value}" for key, value in sonar_props.items()])

            # Run SonarQube scan
            subprocess.run(f"{SONAR_SCANNER} {sonar_args}", shell=True, check=True, cwd=PROJECT_PATH)
            print(f"SonarQube scan completed for PR #{pr_id}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to process PR #{pr_id}: {e}")

# Main loop
while True:
    print("Starting polling...")
    fetch_open_prs()
    process_prs()
    print("Waiting for the next poll...")
    time.sleep(POLL_INTERVAL)
