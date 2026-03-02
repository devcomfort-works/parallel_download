"""Directory and filesystem related management."""

from pathlib import Path
from shutil import rmtree
from typing import Union

from parallel_download.errors.download_errors import DirectoryPermissionError


class Directory:
    """
    A class to manage directory operations.
    디렉토리 작업을 관리하는 클래스입니다.

    Attributes
    ----------
    path : Path
        The path to the managed directory.
        관리되는 디렉토리의 경로입니다.
    """

    def __init__(self, path: Union[str, Path]):
        """
        Initialize the Directory manager.
        Directory 매니저를 초기화합니다.

        Parameters
        ----------
        path : Union[str, Path]
            The target directory path.
            대상 디렉토리 경로입니다.
        """
        self.path = Path(path)

    def ensure(self) -> bool:
        """
        Ensure that the directory exists, creating it if necessary.
        디렉토리가 존재하는지 확인하고, 필요한 경우 생성합니다.

        Creates the directory with all necessary parent directories.
        필요한 모든 상위 디렉토리를 포함하여 디렉토리를 생성합니다.

        Returns
        -------
        bool
            True if the directory exists (or was created), False otherwise.
            디렉토리가 존재하거나 생성되었으면 True, 그렇지 않으면 False를 반환합니다.

        Raises
        ------
        DirectoryPermissionError
            If the directory cannot be created due to insufficient permissions.
            권한 부족으로 디렉토리를 생성할 수 없을 때 발생합니다.
        """
        try:
            self.path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise DirectoryPermissionError(path=str(self.path), original_error=e) from e
        return self.path.is_dir()

    def clear(self, reset: bool = False) -> bool:
        """
        Empty the directory or initialize it.
        디렉토리의 내용을 비우거나 초기화합니다.

        Parameters
        ----------
        reset : bool, optional
            If True, removes the directory completely and recreates it.
            If False, does nothing if directory exists (placeholder for future logic).
            True이면 디렉토리를 완전히 삭제하고 재생성합니다.
            False이면 아무 작업도 하지 않습니다.

        Returns
        -------
        bool
            True if the directory exists, False if it doesn't exist contextually.
            디렉토리가 존재하면 True를 반환합니다.
        """
        if self.path.is_dir():
            if reset:
                rmtree(self.path)
                self.path.mkdir(parents=True, exist_ok=True)
            return True
        return False
