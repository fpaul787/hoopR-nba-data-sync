Project: NBA Data Sync Service

Build a Python-based data synchronization service that keeps an Azure Blob Storage container synchronized with NBA parquet datasets from the GitHub repository sportsdataverse/hoopR-nba-data.

Functional Requirements
Connect to the GitHub API and retrieve all parquet files from the nba directory.
For each file, retrieve:
File name
SHA hash
Download URL
Connect to Azure Blob Storage.
For each source file:
Check whether the corresponding blob exists.
If the blob does not exist, download and upload the file.
If the blob exists, compare the GitHub SHA hash to a github_sha metadata value stored on the blob.
If the SHA values match, skip processing.
If the SHA values differ, download the latest file, overwrite the blob, and update the metadata.
Store the GitHub SHA as blob metadata after every successful upload.
Log all operations, including:
Files discovered
Files skipped
Files uploaded
Errors
Generate a summary at the end of each run showing:
Total files scanned
New files uploaded
Updated files uploaded
Files skipped
Total execution time
Support both local execution and automated execution through GitHub Actions.
Architecture
GitHub Repository
       ↓
GitHub API Client
       ↓
File Discovery
       ↓
SHA Comparison
       ↓
Download Changed Files
       ↓
Azure Blob Upload
       ↓
Update Blob Metadata (github_sha)
       ↓
Execution Summary
Non-Functional Requirements
Use Python 3.12+
Use the Azure Storage Blob SDK
Use the GitHub REST API
Organize code into modules:
github_client.py
storage_client.py
sync_service.py
models.py
config.py
Use structured logging.
Support configuration through environment variables.
Include a GitHub Actions workflow that runs daily and can also be triggered manually.
Goal

Create an incremental file synchronization service that transfers only new or modified parquet files from GitHub to Azure Blob Storage, using GitHub SHA hashes for change detection and Azure Blob metadata for state tracking.