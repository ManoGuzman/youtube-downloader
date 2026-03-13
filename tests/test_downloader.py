"""Unit tests for downloader.py validation functions."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vdl.downloader import DownloadConfig, YouTubeDownloader


class TestValidateUrl:
    """Tests for validate_url method."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PL123456",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=abc_DEF123",
        ],
    )
    def test_validate_url_with_valid_youtube_links(
        self, downloader: YouTubeDownloader, url: str
    ) -> None:
        """Test that valid YouTube URLs are accepted."""
        assert downloader.validate_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.facebook.com/watch?v=123456789",
            "https://www.facebook.com/user/videos/123456789",
            "https://fb.watch/abc123",
            "https://www.facebook.com/page/videos/987654321",
        ],
    )
    def test_validate_url_with_valid_facebook_links(
        self, downloader: YouTubeDownloader, url: str
    ) -> None:
        """Test that valid Facebook URLs are accepted."""
        assert downloader.validate_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "",
            None,
            "not-a-url",
            "https://www.youtube.com/",
            "https://youtube.com/watch",
            "https://youtu.be/",
            "https://www.youtube.com/playlist",
            "https://www.facebook.com/",
            "https://facebook.com",
            "https://example.com/video",
            "http://localhost/video",
            "ftp://youtube.com/video",
        ],
    )
    def test_validate_url_with_invalid_urls(
        self, downloader: YouTubeDownloader, url: str
    ) -> None:
        """Test that invalid URLs are rejected."""
        assert downloader.validate_url(url) is False

    def test_validate_url_case_insensitive(self, downloader: YouTubeDownloader) -> None:
        """Test that URL validation is case insensitive."""
        assert downloader.validate_url("HTTPS://WWW.YOUTUBE.COM/WATCH?v=ABC") is True
        assert downloader.validate_url("HTTP://WWW.YOUTUBE.COM/WATCH?v=ABC") is True


class TestCleanTitle:
    """Tests for clean_title method."""

    def test_clean_title_with_valid_title(self, downloader: YouTubeDownloader) -> None:
        """Test that valid titles are cleaned properly."""
        result = downloader.clean_title("My Video Title")
        assert result == "My Video Title"

    def test_clean_title_removes_official_video(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test removal of official video/audio markers."""
        result = downloader.clean_title("Song Name (Official Video)")
        assert result == "Song Name"
        result = downloader.clean_title("Song Name (official audio)")
        assert result == "Song Name"

    def test_clean_title_removes_lyrics(self, downloader: YouTubeDownloader) -> None:
        """Test removal of lyrics markers."""
        result = downloader.clean_title("Song Name Lyric Video")
        assert result == "Song Name"
        result = downloader.clean_title("Song Name (Lyrics)")
        assert result == "Song Name"

    def test_clean_title_removes_hd_4k(self, downloader: YouTubeDownloader) -> None:
        """Test removal of HD/4K markers."""
        result = downloader.clean_title("Video (HD)")
        assert result == "Video"
        result = downloader.clean_title("Video (4k)")
        assert result == "Video"

    def test_clean_title_removes_brackets(self, downloader: YouTubeDownloader) -> None:
        """Test removal of bracket content."""
        result = downloader.clean_title("Video [2024]")
        assert result == "Video"

    def test_clean_title_removes_path_traversal(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test removal of path traversal attempts."""
        result = downloader.clean_title("Video../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_clean_title_removes_invalid_filename_chars(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test removal of invalid filename characters."""
        result = downloader.clean_title('Video<>:"/\\|?*Title')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_clean_title_empty_parentheses(self, downloader: YouTubeDownloader) -> None:
        """Test removal of empty parentheses."""
        result = downloader.clean_title("Video () ()")
        assert "()" not in result

    def test_clean_title_multiple_spaces(self, downloader: YouTubeDownloader) -> None:
        """Test normalization of multiple spaces."""
        result = downloader.clean_title("Video    Title   Here")
        assert "  " not in result

    def test_clean_title_empty_string_returns_untitled(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that empty string returns 'untitled'."""
        result = downloader.clean_title("")
        assert result == "untitled"

    def test_clean_title_none_returns_untitled(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that None returns 'untitled'."""
        result = downloader.clean_title(None)  # type: ignore
        assert result == "untitled"

    def test_clean_title_non_string_returns_untitled(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that non-string input returns 'untitled'."""
        result = downloader.clean_title(123)  # type: ignore
        assert result == "untitled"

    def test_clean_title_max_length(self, downloader: YouTubeDownloader) -> None:
        """Test that title is truncated to max length."""
        long_title = "A" * 600
        result = downloader.clean_title(long_title)
        assert len(result) <= downloader.config.max_filename_length


class TestGetVideoFormatSelector:
    """Tests for get_video_format_selector method."""

    def test_format_selector_best(self, downloader: YouTubeDownloader) -> None:
        """Test format selector for 'best' quality."""
        result = downloader.get_video_format_selector()
        assert "best" in result.lower()

    def test_format_selector_worst(self, downloader: YouTubeDownloader) -> None:
        """Test format selector for 'worst' quality."""
        downloader.config.video_quality = "worst"
        result = downloader.get_video_format_selector()
        assert "worst" in result.lower()

    def test_format_selector_specific_resolution(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test format selector for specific resolution."""
        downloader.config.video_quality = "720p"
        result = downloader.get_video_format_selector()
        assert "720p" in result

    def test_format_selector_best_with_filter(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test format selector with custom filter."""
        downloader.config.video_quality = "best[height>=1080]"
        result = downloader.get_video_format_selector()
        assert "best" in result.lower()
        assert "1080" in result


class TestGetVideoInfo:
    """Tests for get_video_info method."""

    def test_get_video_info_with_invalid_empty_url(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            downloader.get_video_info("")

    def test_get_video_info_with_invalid_none_url(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that None URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            downloader.get_video_info(None)  # type: ignore

    def test_get_video_info_with_non_string_url(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that non-string URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            downloader.get_video_info(123)  # type: ignore


class TestDownloadWithOpts:
    """Tests for _download_with_opts method."""

    def test_download_with_opts_empty_url_raises_error(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL and download options are required"):
            downloader._download_with_opts("", {}, "MP4")

    def test_download_with_opts_none_url_raises_error(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that None URL raises ValueError."""
        with pytest.raises(ValueError, match="URL and download options are required"):
            downloader._download_with_opts(None, {}, "MP4")  # type: ignore

    def test_download_with_opts_empty_opts_raises_error(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that empty opts raises ValueError."""
        with pytest.raises(ValueError, match="URL and download options are required"):
            downloader._download_with_opts("https://example.com", {}, "MP4")

    def test_download_with_opts_none_opts_raises_error(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that None opts raises ValueError."""
        with pytest.raises(ValueError, match="URL and download options are required"):
            downloader._download_with_opts("https://example.com", None, "MP4")  # type: ignore


class TestCheckFfmpegAvailability:
    """Tests for check_ffmpeg_availability static method."""

    def test_check_ffmpeg_available(self, mock_subprocess: MagicMock) -> None:
        """Test FFmpeg is detected as available."""
        mock_subprocess.run.return_value = MagicMock()
        result = YouTubeDownloader.check_ffmpeg_availability()
        assert result is True
        mock_subprocess.run.assert_called_once()

    def test_check_ffmpeg_not_found(self) -> None:
        """Test FFmpeg is detected as unavailable."""
        with patch("vdl.downloader.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = YouTubeDownloader.check_ffmpeg_availability()
            assert result is False


class TestDownloadConfig:
    """Tests for DownloadConfig dataclass."""

    def test_default_config_values(self) -> None:
        """Test default configuration values."""
        config = DownloadConfig()
        assert config.url_file == "urls.txt"
        assert config.output_path == "downloads"
        assert config.video_quality == "best"
        assert config.mp3_quality == "192"

    def test_custom_config_values(self, temp_dir: Path) -> None:
        """Test custom configuration values."""
        config = DownloadConfig(
            output_path=str(temp_dir / "custom"),
            video_quality="720p",
        )
        assert config.output_path == str(temp_dir / "custom")
        assert config.video_quality == "720p"

    def test_video_path_property(self, temp_dir: Path) -> None:
        """Test video_path property returns correct path."""
        config = DownloadConfig(output_path=str(temp_dir))
        assert config.video_path == str(temp_dir / "video")

    def test_audio_path_property(self, temp_dir: Path) -> None:
        """Test audio_path property returns correct path."""
        config = DownloadConfig(output_path=str(temp_dir))
        assert config.audio_path == str(temp_dir / "audio")


class TestProcessUrl:
    """Tests for process_url method."""

    def test_process_url_invalid_url_returns_false(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test that invalid URL returns False."""
        result = downloader.process_url("not-a-valid-url")
        assert result is False

    def test_process_url_valid_youtube_url(self, downloader: YouTubeDownloader) -> None:
        """Test valid YouTube URL is processed."""
        with patch.object(
            downloader, "download_video_and_audio", return_value=True
        ) as mock:
            result = downloader.process_url("https://www.youtube.com/watch?v=abc")
            assert result is True
            mock.assert_called_once()

    def test_process_url_valid_facebook_url(
        self, downloader: YouTubeDownloader
    ) -> None:
        """Test valid Facebook URL is processed."""
        with patch.object(
            downloader, "download_video_and_audio", return_value=True
        ) as mock:
            result = downloader.process_url("https://www.facebook.com/watch?v=123")
            assert result is True
            mock.assert_called_once()
