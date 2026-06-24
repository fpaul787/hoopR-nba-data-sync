"""Incremental GitHub-to-Blob parquet sync entrypoint."""

from __future__ import annotations

import json
import logging
import os
import time

from github_client import build_default_client
import requests

from storage_client import build_storage_client_from_env


def _download_file_content(url: str, timeout: int = 120) -> bytes:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    start_time = time.perf_counter()
    branch = os.getenv("GITHUB_BRANCH", "main")
    base_path = os.getenv("GITHUB_BASE_PATH", "nba/team_box/parquet")
    max_files_env = os.getenv("SYNC_MAX_FILES")
    max_files = int(max_files_env) if max_files_env else None

    github_client = build_default_client()
    storage_client = build_storage_client_from_env()

    files = github_client.list_parquet_files(base_path=base_path, branch=branch)
    if max_files is not None:
        files = files[:max_files]

    logging.info("discovered_parquet_files=%s base_path=%s branch=%s", len(files), base_path, branch)

    new_files_uploaded = 0
    updated_files_uploaded = 0
    skipped_files = 0
    errored_files = 0

    for source_file in files:
        blob_name = storage_client.map_source_path_to_blob_name(source_file.path)

        try:
            if not storage_client.blob_exists(blob_name):
                content = _download_file_content(source_file.download_url)
                storage_client.upload_with_github_sha(
                    blob_name=blob_name,
                    content=content,
                    github_sha=source_file.sha,
                    overwrite=True,
                )
                new_files_uploaded += 1
                logging.info(
                    "file_uploaded_new source_path=%s blob_name=%s sha=%s",
                    source_file.path,
                    blob_name,
                    source_file.sha,
                )
                continue

            existing_sha = storage_client.get_blob_github_sha(blob_name)
            if existing_sha == source_file.sha:
                skipped_files += 1
                logging.info(
                    "file_skipped_unchanged source_path=%s blob_name=%s sha=%s",
                    source_file.path,
                    blob_name,
                    source_file.sha,
                )
                continue

            content = _download_file_content(source_file.download_url)
            storage_client.upload_with_github_sha(
                blob_name=blob_name,
                content=content,
                github_sha=source_file.sha,
                overwrite=True,
            )
            updated_files_uploaded += 1
            logging.info(
                "file_uploaded_updated source_path=%s blob_name=%s old_sha=%s new_sha=%s",
                source_file.path,
                blob_name,
                existing_sha,
                source_file.sha,
            )
        except Exception:
            errored_files += 1
            logging.exception(
                "file_sync_error source_path=%s blob_name=%s",
                source_file.path,
                blob_name,
            )

    elapsed_seconds = time.perf_counter() - start_time
    summary = {
        "total_files_scanned": len(files),
        "new_files_uploaded": new_files_uploaded,
        "updated_files_uploaded": updated_files_uploaded,
        "files_skipped": skipped_files,
        "files_errored": errored_files,
        "execution_time_seconds": round(elapsed_seconds, 3),
    }

    logging.info("sync_summary %s", json.dumps(summary))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
