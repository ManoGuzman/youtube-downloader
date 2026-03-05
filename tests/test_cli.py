"""Unit tests for cli.py validation functions."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

import pytest

from vdl.cli import app
from vdl.downloader import YouTubeDownloader


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CliRunner instance."""
    return CliRunner()


@pytest.fixture
def temp_dir() -> Any:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_url_file(temp_dir: Any) -> Path:
    """Create a temporary URL file."""
    url_file = temp_dir / "urls.txt"
    url_file.write_text("https://www.youtube.com/watch?v=abc123\n")
    return url_file


class TestCliMutuallyExclusiveOptions:
    """Tests for mutually exclusive --mp3 and --mp4 options."""

    def test_cli_fails_with_both_mp3_and_mp4_flags(self, cli_runner: CliRunner) -> None:
        """Test that using both --mp3 and --mp4 raises error."""
        result = cli_runner.invoke(
            app,
            ["https://example.com/video", "--mp3", "--mp4"],
        )
        assert result.exit_code == 1
        assert "Cannot use both --mp3 and --mp4" in result.output

    def test_cli_succeeds_with_only_mp3_flag(self, cli_runner: CliRunner) -> None:
        """Test that using only --mp3 works."""
        with patch.object(YouTubeDownloader, "process_url", return_value=True):
            result = cli_runner.invoke(
                app,
                ["https://www.youtube.com/watch?v=abc", "--mp3"],
            )
            assert result.exit_code == 0

    def test_cli_succeeds_with_only_mp4_flag(self, cli_runner: CliRunner) -> None:
        """Test that using only --mp4 works."""
        with patch.object(YouTubeDownloader, "process_url", return_value=True):
            result = cli_runner.invoke(
                app,
                ["https://www.youtube.com/watch?v=abc", "--mp4"],
            )
            assert result.exit_code == 0


class TestCliFormatsOption:
    """Tests for --formats option validation."""

    def test_cli_formats_requires_url(self, cli_runner: CliRunner) -> None:
        """Test that --formats without URL raises error."""
        result = cli_runner.invoke(app, ["--formats"])
        assert result.exit_code == 1
        assert "--formats requires a URL" in result.output

    def test_cli_formats_with_url_calls_downloader(self, cli_runner: CliRunner) -> None:
        """Test that --formats with URL calls show_available_formats."""
        with patch.object(YouTubeDownloader, "show_available_formats") as mock_formats:
            cli_runner.invoke(
                app,
                ["--formats", "https://www.youtube.com/watch?v=abc"],
            )
            mock_formats.assert_called_once_with("https://www.youtube.com/watch?v=abc")


class TestCliSetupOption:
    """Tests for --setup option."""

    def test_cli_setup_calls_ffmpeg_help(self, cli_runner: CliRunner) -> None:
        """Test that --setup calls show_ffmpeg_setup_help."""
        with patch.object(YouTubeDownloader, "show_ffmpeg_setup_help") as mock_help:
            cli_runner.invoke(app, ["--setup"])
            mock_help.assert_called_once()


class TestCliUrlAndFileValidation:
    """Tests for URL and file validation."""

    def test_cli_processes_single_url(self, cli_runner: CliRunner) -> None:
        """Test that a single URL is processed."""
        with patch.object(
            YouTubeDownloader, "process_url", return_value=True
        ) as mock_process:
            cli_runner.invoke(
                app,
                ["https://www.youtube.com/watch?v=abc"],
            )
            mock_process.assert_called_once_with("https://www.youtube.com/watch?v=abc")

    def test_cli_processes_url_file(
        self, cli_runner: CliRunner, temp_url_file: Path
    ) -> None:
        """Test that URL file is processed when file exists."""
        with patch.object(YouTubeDownloader, "process_url_file") as mock_file:
            cli_runner.invoke(app, ["--file", str(temp_url_file)])
            mock_file.assert_called_once_with(str(temp_url_file))

    def test_cli_fails_when_url_file_not_found(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test that error is raised when URL file doesn't exist."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        result = cli_runner.invoke(app, ["--file", str(nonexistent_file)])
        assert result.exit_code == 1
        assert "URL file not found" in result.output


class TestCliExceptionHandling:
    """Tests for CLI exception handling."""

    def test_cli_handles_downloader_exception(self, cli_runner: CliRunner) -> None:
        """Test that downloader exceptions are caught and displayed."""
        with patch.object(
            YouTubeDownloader,
            "process_url",
            side_effect=Exception("Download failed"),
        ):
            result = cli_runner.invoke(
                app,
                ["https://www.youtube.com/watch?v=abc"],
            )
            assert result.exit_code == 1
            assert "ERROR:" in result.output


class TestCliDefaultOptions:
    """Tests for CLI default options."""

    def test_cli_default_quality_is_best(self, cli_runner: CliRunner) -> None:
        """Test that default quality is 'best'."""
        with patch.object(YouTubeDownloader, "process_url", return_value=True):
            with patch("vdl.cli.YouTubeDownloader") as MockDownloader:
                mock_instance = MagicMock()
                mock_instance.process_url.return_value = True
                MockDownloader.return_value = mock_instance
                cli_runner.invoke(app, ["https://www.youtube.com/watch?v=abc"])
                MockDownloader.assert_called_once()
                call_kwargs = MockDownloader.call_args[0][0]
                assert call_kwargs.video_quality == "best"

    def test_cli_custom_quality_option(self, cli_runner: CliRunner) -> None:
        """Test that custom quality option works."""
        with patch("vdl.cli.YouTubeDownloader") as MockDownloader:
            mock_instance = MagicMock()
            mock_instance.process_url.return_value = True
            MockDownloader.return_value = mock_instance
            cli_runner.invoke(
                app,
                ["https://www.youtube.com/watch?v=abc", "--quality", "720p"],
            )
            MockDownloader.assert_called_once()
            call_kwargs = MockDownloader.call_args[0][0]
            assert call_kwargs.video_quality == "720p"

    def test_cli_default_output_directory(self, cli_runner: CliRunner) -> None:
        """Test that default output directory is 'downloads'."""
        with patch("vdl.cli.YouTubeDownloader") as MockDownloader:
            mock_instance = MagicMock()
            mock_instance.process_url.return_value = True
            MockDownloader.return_value = mock_instance
            cli_runner.invoke(app, ["https://www.youtube.com/watch?v=abc"])
            MockDownloader.assert_called_once()
            call_kwargs = MockDownloader.call_args[0][0]
            assert call_kwargs.output_path == "downloads"

    def test_cli_custom_output_directory(self, cli_runner: CliRunner) -> None:
        """Test that custom output directory option works."""
        with patch.object(YouTubeDownloader, "process_url", return_value=True):
            with patch("vdl.downloader.Path.mkdir"):
                result = cli_runner.invoke(
                    app,
                    [
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "--output",
                        "custom/path",
                    ],
                )
                assert result.exit_code == 0
