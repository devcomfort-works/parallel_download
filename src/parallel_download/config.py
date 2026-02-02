"""
Download configuration recipes for different scenarios.
다양한 시나리오에 따른 다운로드 설정 레시피를 정의합니다.
"""

from dataclasses import dataclass
from typing import Literal

TimeoutRecipe = Literal["FOR_LARGE_FILES", "BALANCED", "FOR_SMALL_FILES"]


@dataclass
class DownloadConfig:
    """
    Configuration for download behavior.
    다운로드 동작에 대한 설정입니다.

    Attributes
    ----------
    timeout : int
        The maximum time in seconds to wait for a download to complete.
        다운로드가 완료될 때까지 대기할 최대 시간(초)입니다.
    description : str
        A human-readable description of the configuration's purpose.
        해당 설정의 목적에 대한 설명입니다.
    """

    timeout: int
    description: str


# Predefined recipes for different download scenarios
# 다양한 다운로드 시나리오를 위해 미리 정의된 레시피들입니다.
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
