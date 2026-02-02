"""Tests for Directory class."""

from pathlib import Path
import tempfile
from parallel_download.filesystem.directory import Directory


class TestDirectoryEnsure:
    """Tests for Directory.ensure method."""

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
    """Tests for Directory.clear method."""

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
