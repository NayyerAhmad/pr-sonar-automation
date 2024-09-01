# Bitbucket PR Automation

Automates fetching open PRs from a Bitbucket repository, checking out each PR branch, and running SonarQube scans.

## Requirements

- Python 3.x
- `requests` and `python-dotenv` libraries
- Access to Bitbucket API
- SonarQube Scanner

## Setup

1. **Install dependencies:**

    ```bash
    pip install requests python-dotenv
    ```

2. **Create a `.env` file** with the following configuration:

    ```ini
    # Bitbucket Configuration
    BITBUCKET_REPO=your-bitbucket-repo
    BITBUCKET_USER=your-bitbucket-username
    BITBUCKET_TOKEN=your-bitbucket-token

    # SonarQube Configuration
    SONAR_SCANNER=path-to-your-sonar-scanner
    SONAR_PROJECT_PROPERTIES=path-to-your-sonar-project-properties

    # Polling Interval (in seconds)
    POLL_INTERVAL=3600

    # Project Directory
    PROJECT_PATH=/path/to/your/project
    ```

3. **Run the script:**

    ```bash
    python main.py
    ```
