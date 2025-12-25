from pathlib import Path
from shutil import rmtree


def ensure_directory(path: Path) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.

    Creates the directory at the specified path with all parent directories
    as needed.

    Parameters
    ----------
    path : Path
        The path to the directory to create or verify.

    Returns
    -------
    bool
        True if the directory exists after execution, False otherwise.
    """
    path.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
    return path.is_dir()  # 디렉토리 존재 여부 반환


def clear_directory(path: Path, recreate: bool = False) -> bool:
    """
    Clear the contents of a directory or recreate it.

    If the directory exists, optionally removes it completely and recreates
    it from scratch. If recreate is False, does nothing.

    Parameters
    ----------
    path : Path
        The path to the directory to clear.
    recreate : bool, optional
        If True, removes the entire directory and creates an empty one.
        If False, does nothing. Default is False.

    Returns
    -------
    bool
        True if the directory was successfully cleared/recreated, False if
        the directory did not exist.
    """
    if path.is_dir():  # 디렉토리 존재 여부 확인
        if recreate:  # 재생성 여부 확인
            rmtree(path)  # 디렉토리 삭제
            path.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
        return True  # 디렉토리 존재 여부 반환
    return False  # 디렉토리 존재 여부 반환
