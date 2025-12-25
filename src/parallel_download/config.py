"""Download configuration recipes for different scenarios."""

from dataclasses import dataclass
from typing import Literal

TimeoutRecipe = Literal["FOR_LARGE_FILES", "BALANCED", "FOR_SMALL_FILES"]


@dataclass
class DownloadConfig:
    """Configuration for download behavior."""

    timeout: int
    description: str


# Predefined recipes for different download scenarios
DOWNLOAD_RECIPES: dict[TimeoutRecipe, DownloadConfig] = {
    "FOR_LARGE_FILES": DownloadConfig(
        timeout=300,  # 5 minutes
        description="For downloading large files (several GB to tens of GB). "
        "Uses longer timeout and lower concurrency.",
    ),
    "BALANCED": DownloadConfig(
        timeout=60,  # 1 minute
        description="Balanced configuration for mixed file sizes.",
    ),
    "FOR_SMALL_FILES": DownloadConfig(
        timeout=15,  # 15 seconds
        description="For downloading small files (KB-MB range). "
        "Uses shorter timeout for faster feedback.",
    ),
}
