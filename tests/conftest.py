"""Pytest configuration and fixtures for video downloader tests."""

import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from vdl.downloader import YouTubeDownloader, DownloadConfig


@pytest.fixture
def temp_dir() -> Generator[Any, None, None]:
    """Create a temporary directory for test file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def download_config(temp_dir: Path) -> DownloadConfig:
    """Create a DownloadConfig with temporary directory paths."""
    return DownloadConfig(
        url_file="urls.txt",
        output_path=str(temp_dir / "downloads"),
        log_file=str(temp_dir / "test.log"),
    )


@pytest.fixture
def downloader(download_config: DownloadConfig) -> YouTubeDownloader:
    """Create a YouTubeDownloader instance with test config."""
    return YouTubeDownloader(download_config)


@pytest.fixture
def mock_yt_dlp() -> Generator[MagicMock, None, None]:
    """Create a mock for yt_dlp module."""
    with patch("vdl.downloader.yt_dlp") as mock:
        yield mock


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Create a mock for subprocess module."""
    with patch("vdl.downloader.subprocess") as mock:
        yield mock


@pytest.fixture
def sample_video_info() -> dict:
    """Sample video info dictionary from yt-dlp."""
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Test Video Title",
        "duration": 180,
        "view_count": 10000,
        "formats": [
            {
                "format_id": "137",
                "vcodec": "avc1.64001f",
                "height": 1080,
                "fps": 30,
                "filesize": 50000000,
            },
            {
                "format_id": "136",
                "vcodec": "avc1.64001e",
                "height": 720,
                "fps": 30,
                "filesize": 30000000,
            },
            {
                "format_id": "140",
                "vcodec": "none",
                "acodec": "mp4a.40.2",
                "filesize": 5000000,
            },
        ],
    }


VALID_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/playlist?list=PL123456",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
]

INVALID_YOUTUBE_URLS = [
    "https://www.youtube.com/",  # Missing video ID
    "https://youtube.com/",  # Missing www and video ID
    "not-a-url",
    "",
    "https://example.com/video",
]

VALID_FACEBOOK_URLS = [
    "https://www.facebook.com/watch?v=123456789",
    "https://www.facebook.com/user/videos/123456789",
    "https://fb.watch/abc123",
]

INVALID_FACEBOOK_URLS = [
    "https://www.facebook.com/",
    "https://facebook.com/",
    "not-a-fb-url",
]
