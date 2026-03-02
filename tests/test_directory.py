"""Filesystem Directory 유틸리티의 생성/정리 동작을 검증하는 테스트 모음."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from parallel_download.errors.download_errors import DirectoryPermissionError
from parallel_download.filesystem.directory import Directory


class TestDirectoryEnsure:
    """`Directory.ensure()`가 경로를 안전하게 보장하는지 검증한다."""

    def test_ensure_existing_directory(self):
        """Test ensure on existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            d = Directory(path)
            result = d.ensure()

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_creates_new_directory(self):
        """Test ensure creates new directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "new_dir"
            assert not path.exists()

            d = Directory(path)
            result = d.ensure()

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_creates_nested_directories(self):
        """Test ensure creates nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "a" / "b" / "c" / "d"
            assert not path.exists()

            d = Directory(path)
            result = d.ensure()

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_directory_with_string_path(self):
        """Test ensure with string path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path_str = str(Path(tmpdir) / "from_string")
            d = Directory(path_str)
            result = d.ensure()

            assert result is True
            assert Path(path_str).exists()
            assert Path(path_str).is_dir()


class TestDirectoryClear:
    """`Directory.clear()`의 reset 옵션별 동작을 검증한다."""

    def test_clear_existing_directory_no_reset(self):
        """Test clear on existing directory with reset=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            # Create a dummy file
            (path / "file.txt").touch()

            d = Directory(path)
            result = d.clear(reset=False)

            assert result is True
            assert path.exists()
            assert (path / "file.txt").exists()  # Should not be deleted

    def test_clear_non_existing_directory(self):
        """Test clear on non-existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ghost"

            d = Directory(path)
            result = d.clear(reset=False)

            assert result is False
            assert not path.exists()

    def test_clear_reset_removes_contents(self):
        """Test clear with reset=True removes contents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "target"
            path.mkdir()
            (path / "file1.txt").touch()
            (path / "subdir").mkdir()
            (path / "subdir" / "file2.txt").touch()

            d = Directory(path)
            result = d.clear(reset=True)

            assert result is True
            assert path.exists()
            assert not (path / "file1.txt").exists()
            assert not (path / "subdir").exists()
            # Check if directory is empty
            assert len(list(path.iterdir())) == 0


class TestDirectoryEnsureErrorWrapping:
    """`Directory.ensure()`의 PermissionError 도메인 에러 래핑을 검증한다."""

    def test_ensure_permission_error_raises_domain_error(self):
        """PermissionError 발생 시 DirectoryPermissionError로 래핑되는지 확인."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "restricted"
            d = Directory(path)

            with patch.object(Path, "mkdir", side_effect=PermissionError("Permission denied")):
                with pytest.raises(DirectoryPermissionError) as exc_info:
                    d.ensure()

                assert str(path) in str(exc_info.value)
                assert exc_info.value.path == str(path)
                assert isinstance(exc_info.value.original_error, PermissionError)
                assert exc_info.value.__cause__ is exc_info.value.original_error

    def test_ensure_on_non_existing_nested_path(self):
        """깊은 중첩 경로(a/b/c/d/e)에서 ensure() 후 디렉토리 존재 확인."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "a" / "b" / "c" / "d" / "e"
            assert not path.exists()

            d = Directory(path)
            result = d.ensure()

            assert result is True
            assert path.exists()
            assert path.is_dir()
