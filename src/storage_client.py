"""Azure Blob storage client outline for sync operations."""

from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class StorageConfig:
    """Runtime configuration for Azure Blob storage access."""

    account_url: str
    container_name: str
    credential: str | None = None
    metadata_sha_key: str = "github_sha"


class StorageClient:
    """Operations required by the sync service for blob state tracking."""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        self.account_url = config.account_url
        self.container_name = config.container_name
        self.credential = config.credential
        self.metadata_sha_key = config.metadata_sha_key

    def blob_exists(self, blob_name: str) -> bool:
        """Return whether the target blob currently exists."""

        raise NotImplementedError()

    def get_blob_metadata(self, blob_name: str) -> dict[str, str]:
        """Fetch blob metadata for a given blob name."""

        raise NotImplementedError()

    def get_blob_github_sha(self, blob_name: str) -> str | None:
        """Return the stored GitHub SHA metadata value, if present."""

        raise NotImplementedError()

    def upload_blob_bytes(
        self, blob_name: str, content: bytes, overwrite: bool = True
    ) -> None:
        """Upload bytes to blob storage."""

        raise NotImplementedError()

    def set_blob_metadata(self, blob_name: str, metadata: dict[str, str]) -> None:
        """Set blob metadata for a blob."""

        raise NotImplementedError()

    def upload_with_github_sha(
        self,
        blob_name: str,
        content: bytes,
        github_sha: str,
        overwrite: bool = True,
    ) -> None:
        """Upload content and apply SHA metadata as one sync operation."""

        raise NotImplementedError()

    def map_source_path_to_blob_name(
        self, source_path: str, strip_prefix: str = "nba/"
    ) -> str:
        """Map GitHub source path to destination blob name."""

        raise NotImplementedError()


def build_storage_config_from_env() -> StorageConfig:
    """Create storage config from environment variables."""

    load_dotenv()

    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL", "")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "")
    credential = os.getenv("AZURE_STORAGE_CREDENTIAL")

    return StorageConfig(
        account_url=account_url,
        container_name=container_name,
        credential=credential,
        metadata_sha_key="github_sha",
    )


def build_storage_client_from_env() -> StorageClient:
    """Create storage client from environment variables."""

    return StorageClient(config=build_storage_config_from_env())
