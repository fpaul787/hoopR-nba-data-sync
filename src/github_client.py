"""GitHub API client for parquet file discovery."""

from __future__ import annotations

from dataclasses import dataclass
import os
import time
from typing import Any

from dotenv import load_dotenv
import requests


GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
RETRYABLE_STATUS_CODES = {500, 502, 503, 504}


@dataclass(frozen=True)
class GitHubParquetFile:
    """Metadata required to sync a parquet file."""

    name: str
    path: str
    sha: str
    download_url: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
            "sha": self.sha,
            "download_url": self.download_url,
        }


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    def __init__(
        self,
        owner: str,
        repo: str,
        token: str | None = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay_seconds: float = 2.0,
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _request_with_retry(self, url: str) -> requests.Response:
        last_response: requests.Response | None = None

        for attempt in range(1, self.retry_attempts + 1):
            response = self.session.get(url, timeout=self.timeout)
            last_response = response

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.retry_attempts:
                time.sleep(self.retry_delay_seconds)
                continue

            response.raise_for_status()
            return response

        if last_response is None:
            raise RuntimeError("GitHub request did not return a response")

        last_response.raise_for_status()
        return last_response

    def _get_json(self, url: str) -> Any:
        response = self._request_with_retry(url)
        response.raise_for_status()
        return response.json()

    def _list_contents(self, path: str, branch: str) -> list[dict[str, Any]]:
        encoded_path = path.strip("/")
        url = f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/contents/{encoded_path}?ref={branch}"
        data = self._get_json(url)

        if isinstance(data, list):
            return data
        return [data]

    def list_parquet_files(
        self,
        base_path: str = "nba/team_box/parquet",
        branch: str = "main",
    ) -> list[GitHubParquetFile]:
        """Return all parquet files under a path in the repository."""

        parquet_files: list[GitHubParquetFile] = []
        pending_paths = [base_path.strip("/")]

        while pending_paths:
            current_path = pending_paths.pop()
            entries = self._list_contents(path=current_path, branch=branch)

            for entry in entries:
                entry_type = entry.get("type")
                entry_path = entry.get("path")
                if not entry_path:
                    continue

                if entry_type == "dir":
                    pending_paths.append(entry_path)
                    continue

                if entry_type != "file":
                    continue
                if not entry_path.endswith(".parquet"):
                    continue

                parquet_files.append(
                    GitHubParquetFile(
                        name=entry_path.rsplit("/", 1)[-1],
                        path=entry_path,
                        sha=entry["sha"],
                        download_url=entry.get("download_url")
                        or f"{RAW_BASE}/{self.owner}/{self.repo}/{branch}/{entry_path}",
                    )
                )

        parquet_files.sort(key=lambda file: file.path)
        return parquet_files


def build_default_client() -> GitHubClient:
    """Create a client configured from environment variables."""

    load_dotenv()

    owner = os.getenv("GITHUB_OWNER", "sportsdataverse")
    repo = os.getenv("GITHUB_REPO", "hoopR-nba-data")
    token = os.getenv("GITHUB_TOKEN")
    return GitHubClient(owner=owner, repo=repo, token=token)
