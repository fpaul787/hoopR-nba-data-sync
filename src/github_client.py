"""GitHub API client for parquet file discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any

import requests


GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"


@dataclass(frozen=True)
class GitHubParquetFile:
	"""Metadata required to sync a parquet file."""

	name: str
	path: str
	sha: str
	download_url: str

	def to_dict(self) -> dict[str, str]:
		return asdict(self)


class GitHubClient:
	"""Thin wrapper around the GitHub REST API."""

	def __init__(self, owner: str, repo: str, token: str | None = None, timeout: int = 30) -> None:
		self.owner = owner
		self.repo = repo
		self.timeout = timeout
		self.session = requests.Session()
		self.session.headers.update(
			{
				"Accept": "application/vnd.github+json",
				"X-GitHub-Api-Version": "2022-11-28",
			}
		)

		if token:
			self.session.headers["Authorization"] = f"Bearer {token}"

	def _get_json(self, url: str) -> Any:
		response = self.session.get(url, timeout=self.timeout)
		response.raise_for_status()
		return response.json()

	def get_branch_commit_sha(self, branch: str = "main") -> str:
		data = self._get_json(f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/branches/{branch}")
		return data["commit"]["sha"]

	def list_parquet_files(
		self,
		base_path: str = "nba/team_box/parquet",
		branch: str = "main",
	) -> list[GitHubParquetFile]:
		"""Return all parquet files under a path in the repository."""

		commit_sha = self.get_branch_commit_sha(branch=branch)
		tree_data = self._get_json(
			f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/git/trees/{commit_sha}?recursive=1"
		)

		normalized_base = base_path.strip("/") + "/"
		parquet_files: list[GitHubParquetFile] = []

		for item in tree_data.get("tree", []):
			path = item.get("path")
			if not path:
				continue
			if item.get("type") != "blob":
				continue
			if not path.startswith(normalized_base):
				continue
			if not path.endswith(".parquet"):
				continue

			parquet_files.append(
				GitHubParquetFile(
					name=path.rsplit("/", 1)[-1],
					path=path,
					sha=item["sha"],
					download_url=f"{RAW_BASE}/{self.owner}/{self.repo}/{branch}/{path}",
				)
			)

		parquet_files.sort(key=lambda file: file.path)
		return parquet_files


def build_default_client() -> GitHubClient:
	"""Create a client configured from environment variables."""

	owner = os.getenv("GITHUB_OWNER", "sportsdataverse")
	repo = os.getenv("GITHUB_REPO", "hoopR-nba-data")
	token = os.getenv("GITHUB_TOKEN")
	return GitHubClient(owner=owner, repo=repo, token=token)
