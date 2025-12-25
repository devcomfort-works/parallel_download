"""Tests for utility functions."""

import pytest
from pathlib import Path
import tempfile

from parallel_download.utils import ensure_directory, clear_directory


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_ensure_existing_directory(self):
        """Test ensure_directory on existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            result = ensure_directory(path)

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_creates_new_directory(self):
        """Test ensure_directory creates new directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "new_dir"
            assert not path.exists()

            result = ensure_directory(path)

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_creates_nested_directories(self):
        """Test ensure_directory creates nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "a" / "b" / "c" / "d"
            assert not path.exists()

            result = ensure_directory(path)

            assert result is True
            assert path.exists()
            assert path.is_dir()

    def test_ensure_directory_with_string_path(self):
        """Test ensure_directory with string path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path_str = str(Path(tmpdir) / "from_string")
            result = ensure_directory(Path(path_str))

            assert result is True
            assert Path(path_str).exists()

    def test_ensure_directory_idempotent(self):
        """Test ensure_directory is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "idempotent_test"

            result1 = ensure_directory(path)
            result2 = ensure_directory(path)
            result3 = ensure_directory(path)

            assert result1 is True
            assert result2 is True
            assert result3 is True


class TestClearDirectory:
    """Tests for clear_directory function."""

    def test_clear_nonexistent_directory(self):
        """Test clear_directory on non-existent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent"
            result = clear_directory(path, recreate=False)

            assert result is False
            assert not path.exists()

    def test_clear_directory_without_recreate(self):
        """Test clear_directory without recreate flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "to_clear"
            path.mkdir()
            (path / "file.txt").write_text("content")
            assert path.exists()

            result = clear_directory(path, recreate=False)

            assert result is True
            assert path.exists()  # Directory still exists
            assert (path / "file.txt").exists()  # Content not removed

    def test_clear_directory_with_recreate(self):
        """Test clear_directory with recreate flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "to_clear"
            path.mkdir()
            (path / "file.txt").write_text("content")
            assert path.exists()
            assert (path / "file.txt").exists()

            result = clear_directory(path, recreate=True)

            assert result is True
            assert path.exists()  # Directory recreated
            assert not (path / "file.txt").exists()  # Content removed

    def test_clear_directory_recreate_nonexistent(self):
        """Test clear_directory recreate on non-existent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent"
            result = clear_directory(path, recreate=True)

            assert result is False
            assert not path.exists()

    def test_clear_directory_nested_content(self):
        """Test clear_directory removes nested content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "to_clear"
            path.mkdir()
            (path / "subdir").mkdir()
            (path / "subdir" / "file.txt").write_text("content")
            (path / "file1.txt").write_text("content1")
            (path / "file2.txt").write_text("content2")

            result = clear_directory(path, recreate=True)

            assert result is True
            assert path.exists()
            assert len(list(path.iterdir())) == 0  # All content removed

    def test_clear_directory_with_symlinks(self):
        """Test clear_directory with symlinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "to_clear"
            path.mkdir()
            target = Path(tmpdir) / "target"
            target.mkdir()
            link = path / "link"
            link.symlink_to(target)

            result = clear_directory(path, recreate=True)

            assert result is True
            assert path.exists()
            assert not link.exists()
            assert target.exists()  # Original target not affected

