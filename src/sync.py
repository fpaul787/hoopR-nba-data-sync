"""Temporary entry point focused on GitHub parquet discovery."""

from __future__ import annotations

import json
import logging
import os

from github_client import build_default_client


def main() -> None:
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

	branch = os.getenv("GITHUB_BRANCH", "main")
	base_path = os.getenv("GITHUB_BASE_PATH", "nba/team_box/parquet")
	client = build_default_client()

	files = client.list_parquet_files(base_path=base_path, branch=branch)
	logging.info("discovered_parquet_files=%s base_path=%s branch=%s", len(files), base_path, branch)

	print(json.dumps([item.to_dict() for item in files], indent=2))


if __name__ == "__main__":
	main()
