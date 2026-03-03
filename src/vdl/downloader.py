#!/usr/bin/env python3
"""
YouTube Downloader
=================
A powerful script to download YouTube videos in MP4 format and extract audio in MP3 format.
Uses yt-dlp and FFmpeg for reliable downloads and high-quality audio conversion.

Author: YouTube Downloader Team
License: MIT
"""

# Standard library imports first
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

# Third-party imports
import yt_dlp


# ============================================================================
# CONFIGURATION SECTION - Modify these settings as needed
# ============================================================================


@dataclass
class DownloadConfig:
    """Configuration settings for YouTube downloader."""

    # File locations
    url_file: str = "urls.txt"
    output_path: str = "downloads"
    log_file: str = "downloader.log"

    # Quality settings
    video_quality: str = "best"
    mp3_quality: str = "192"

    # File naming
    max_filename_length: int = 500

    def __post_init__(self):
        """Ensure output directories exist."""
        Path(self.output_path).mkdir(exist_ok=True)
        Path(self.video_path).mkdir(exist_ok=True)
        Path(self.audio_path).mkdir(exist_ok=True)

    @property
    def video_path(self) -> str:
        """Get full path to video output directory."""
        return os.path.join(self.output_path, "video")

    @property
    def audio_path(self) -> str:
        """Get full path to audio output directory."""
        return os.path.join(self.output_path, "audio")


class DownloadError(Exception):
    """Custom exception for download-related errors."""


class FormatNotAvailableError(DownloadError):
    """Exception for unavailable video formats."""


class YouTubeDownloader:
    """Main YouTube downloader class."""

    YOUTUBE_URL_PATTERNS = [
        r"https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+",
        r"https?://(?:www\.)?youtu\.be/[\w-]+",
        r"https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+",
    ]

    FACEBOOK_URL_PATTERNS = [
        r"https?://(?:www\.|m\.)?facebook\.com/.+/videos/.+",
        r"https?://(?:www\.)?fb\.watch/.+",
        r"https?://(?:www\.)?facebook\.com/watch/?\?v=\d+",
    ]

    TITLE_CLEANUP_PATTERNS = [
        r"\(*\s*official\s+(video|audio)\s*\)*",
        r"\(*\s*(video|audio|vídeo|áudio)\s+oficial\s*\)*",
        r"\(*\s*lyric\s+video\s*\)*",
        r"\(*\s*lyrics?\s*\)*",
        r"\(*\s*letra\s*\)*",
        r"\(*\s*(hd|4k)\s*\)*",
        r"\[.*?\]",
    ]

    def __init__(self, config: Optional[DownloadConfig] = None):
        """Initialize downloader with configuration."""
        self.config = config or DownloadConfig()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging with file and console handlers."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def check_ffmpeg_availability() -> bool:
        """Check if FFmpeg is available in the system PATH."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def show_ffmpeg_setup_help() -> None:
        """Display FFmpeg setup instructions."""
        print(
            f"""
{'='*60}
FFMPEG SETUP REQUIRED
{'='*60}
FFmpeg is required for MP3 audio conversion but was not found.

1. Install FFmpeg:
   Windows: winget install --id=Gyan.FFmpeg
   macOS:   brew install ffmpeg
   Linux:   sudo apt install ffmpeg

2. Restart your terminal and verify:
   ffmpeg -version
{'='*60}
"""
        )

    def clean_title(self, title: str) -> str:
        """Clean video title for use as filename."""
        if not title or not isinstance(title, str):
            return "untitled"

        # Security: remove path traversal attempts
        title = title.replace("..", "").replace("/", "").replace("\\", "")

        # Remove unwanted phrases
        for pattern in self.TITLE_CLEANUP_PATTERNS:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Remove invalid filename characters and normalize spacing
        title = re.sub(r'[<>:"/\\|?*]', "", title)
        title = re.sub(r"\(\s*\)", "", title)
        title = re.sub(r"\s{2,}", " ", title).strip()

        # Ensure valid result with length limit
        title = title or "untitled"
        if len(title) > self.config.max_filename_length:
            title = title[: self.config.max_filename_length].rstrip()

        return title

    def validate_url(self, url: str) -> bool:
        """Validate YouTube or Facebook URL format."""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()

        # Check YouTube patterns
        if any(
            re.match(pattern, url, re.IGNORECASE)
            for pattern in self.YOUTUBE_URL_PATTERNS
        ):
            return True

        # Check Facebook patterns
        if any(
            re.match(pattern, url, re.IGNORECASE)
            for pattern in self.FACEBOOK_URL_PATTERNS
        ):
            return True

        return False

    def get_video_format_selector(self) -> str:
        """Get video format selector based on quality setting."""
        quality = self.config.video_quality

        if quality == "best":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        if quality == "worst":
            return "worst[ext=mp4]/worst"
        if quality.startswith("best[") and quality.endswith("]"):
            filter_part = quality[5:-1]
            return (
                f"bestvideo[{filter_part}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[{filter_part}]+bestaudio/"
                f"best[{filter_part}]/"
                f"bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                f"best"
            )
        return f"{quality}/best"

    def _get_video_info_with_opts(
        self, url: str, ydl_opts: dict
    ) -> Optional[Dict[str, Any]]:
        """Get video information using specified options."""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            self.logger.error("Failed to get video info: %s", error_msg)

            error_messages = {
                "Video unavailable": "Video is unavailable or private",
                "Sign in to confirm your age": "Age-restricted video - authentication required",
                "Private video": "This video is private",
            }

            for key, msg in error_messages.items():
                if key in error_msg:
                    raise DownloadError(msg) from e

            raise DownloadError(
                f"Failed to retrieve video information: {error_msg}"
            ) from e
        except (ValueError, KeyError, TypeError) as e:
            self.logger.error("Error getting video info: %s", e, exc_info=True)
            raise DownloadError(f"Unexpected error: {e}") from e

    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information from URL."""
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL provided")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        return self._get_video_info_with_opts(url, ydl_opts)

    def _extract_quality_info(
        self, format_info: Dict[str, Any]
    ) -> Tuple[str, str, int]:
        """Extract quality information from format dictionary."""
        height = format_info.get("height", "Unknown")
        if height != "Unknown":
            height = str(height)

        fps = format_info.get("fps", "Unknown")
        if fps != "Unknown":
            fps = str(fps)

        filesize = (
            format_info.get("filesize") or format_info.get("filesize_approx") or 0
        )

        return height, fps, filesize

    def get_video_quality_info(self, url: str) -> Tuple[str, str, int]:
        """Get information about the selected video quality."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        try:
            info = self._get_video_info_with_opts(url, ydl_opts)

            if not info:
                self.logger.warning("No video info returned")
                return "Unknown", "Unknown", 0

            formats = info.get("formats", [])
            if not formats:
                return self._extract_quality_info(info)

            # Find best video format
            video_formats = [
                f for f in formats if f.get("vcodec") != "none" and f.get("height")
            ]
            if video_formats:
                best_video = max(video_formats, key=lambda x: x.get("height", 0))
                return self._extract_quality_info(best_video)

            return self._extract_quality_info(info)

        except yt_dlp.DownloadError as e:
            self.logger.warning("Could not get quality info: %s", e)
            return "Unknown", "Unknown", 0

    def show_available_formats(self, url: str) -> None:
        """Display available video formats for debugging purposes."""
        ydl_opts = {"listformats": True, "quiet": False}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError as e:
            print(f"Error getting formats: {e}")
            self.logger.error("Failed to get formats for %s: %s", url, e)

    def _print_video_metadata(self, info: Dict[str, Any]) -> None:
        """Print video metadata."""
        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
        view_count = info.get("view_count", 0)

        # Convert duration to int if it's a float (Facebook videos)
        if isinstance(duration, float):
            duration = int(duration)

        print(f"\nProcessing: {title}")
        print(f"Duration: {duration//60}:{duration%60:02d} | Views: {view_count:,}")

    def _check_existing_files(self, mp4_file: str, mp3_file: str) -> Tuple[bool, bool]:
        """Check which files already exist."""
        return os.path.exists(mp4_file), os.path.exists(mp3_file)

    def _print_quality_info(self, url: str) -> None:
        """Print video quality information."""
        height, fps, filesize = self.get_video_quality_info(url)
        filesize_mb = filesize / (1024 * 1024) if filesize > 0 else 0
        quality_info = f"Available Quality: {height}p @ {fps}fps"
        if filesize_mb > 0:
            quality_info += f" (~{filesize_mb:.1f}MB)"
        print(quality_info)
        print(f"Requesting: {self.config.video_quality}")

    def download_video_and_audio(self, url: str) -> bool:
        """Download video in MP4 format and extract audio as MP3."""
        try:
            print("Fetching video information...")

            info = self._get_and_validate_video_info(url)
            if not info:
                return False

            self._print_video_metadata(info)

            # Prepare file paths with separate folders
            clean = self.clean_title(info.get("title", "Unknown"))
            if clean == "untitled":
                self.logger.warning(
                    "Could not clean title properly: %s", info.get("title")
                )

            mp4_file = os.path.join(self.config.video_path, clean + ".mp4")
            mp3_file = os.path.join(self.config.audio_path, clean + ".mp3")

            # Check if both files exist
            if self._check_both_files_exist(mp4_file, mp3_file):
                return True

            # Download missing files
            success = self._download_missing_files(url, clean, mp4_file, mp3_file)

            if success:
                print("Download completed successfully\n")

            return success

        except KeyboardInterrupt:
            print("\n\nDownload cancelled by user")
            return False
        except (
            DownloadError,
            yt_dlp.DownloadError,
            ValueError,
            TypeError,
            KeyError,
        ) as e:
            return self._handle_download_exception(e, url)

    def _get_and_validate_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get and validate video information, handling errors appropriately."""
        try:
            info = self.get_video_info(url)
            if not info:
                print("ERROR: Failed to get video information")
            return info
        except DownloadError as e:
            print(f"ERROR: {str(e)}")
            return None

    def _handle_download_exception(self, error: Exception, url: str) -> bool:
        """Handle exceptions during download process."""
        if isinstance(error, yt_dlp.DownloadError):
            print(f"ERROR: Download failed: {error}")
            self.logger.error("Download failed for %s: %s", url, error)
        else:
            print(f"ERROR: Unexpected error: {error}")
            self.logger.error("Unexpected error for %s: %s", url, error, exc_info=True)
        return False

    def _check_both_files_exist(self, mp4_file: str, mp3_file: str) -> bool:
        """Check if both MP4 and MP3 files exist."""
        mp4_exists, mp3_exists = self._check_existing_files(mp4_file, mp3_file)

        if mp4_exists and mp3_exists:
            print("Both MP4 and MP3 files already exist - skipping\n")
            return True
        return False

    def _download_missing_files(
        self, url: str, clean: str, mp4_file: str, mp3_file: str
    ) -> bool:
        """Download MP4 and MP3 files if they don't exist."""
        mp4_exists, mp3_exists = self._check_existing_files(mp4_file, mp3_file)

        # Download MP4 if needed
        if not mp4_exists:
            self._print_quality_info(url)
            if not self.download_mp4(url, clean, mp4_file):
                print("MP4 download failed")
                return False
        else:
            print(f"MP4 already exists: {mp4_file} - skipping")

        # Download MP3 if needed
        if not mp3_exists:
            if not self.download_mp3(url, clean, mp3_file):
                print("MP3 download failed")
                return False
        else:
            print(f"MP3 already exists: {mp3_file} - skipping")

        return True

    def _get_base_download_opts(self, clean_filename: str, output_dir: str) -> dict:
        """Get base download options common to all downloads."""
        return {
            "outtmpl": os.path.join(output_dir, clean_filename + ".%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self._progress_hook],
        }

    def download_mp4(self, url: str, clean_filename: str, mp4_file: str) -> bool:
        """Download video in MP4 format."""
        ydl_opts = self._get_base_download_opts(clean_filename, self.config.video_path)
        ydl_opts.update(
            {
                "format": self.get_video_format_selector(),
                "merge_output_format": "mp4",
            }
        )

        try:
            print("Downloading MP4 video...")
            success = self._download_with_opts(url, ydl_opts, "MP4 video")

            if success and os.path.exists(mp4_file):
                file_size = os.path.getsize(mp4_file) / (1024 * 1024)
                print(f"MP4 completed: {mp4_file} ({file_size:.1f}MB)")
            else:
                print(f"Warning: Expected file not found: {mp4_file}")
                success = False

            return success

        except (OSError, IOError, yt_dlp.DownloadError) as e:
            print(f"ERROR downloading MP4: {e}")
            self.logger.error("Error in download_mp4: %s", e, exc_info=True)
            return False

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Hook for download progress updates."""
        if d["status"] == "downloading":
            try:
                percent = d.get("_percent_str", "N/A")
                speed = d.get("_speed_str", "N/A")
                eta = d.get("_eta_str", "N/A")
                print(
                    f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}",
                    end="",
                    flush=True,
                )
            except (KeyError, TypeError, ValueError):
                pass
        elif d["status"] == "finished":
            print()

    def download_mp3(self, url: str, clean_filename: str, mp3_file: str) -> bool:
        """Download and convert audio to MP3 format."""
        try:
            if not self.check_ffmpeg_availability():
                print("ERROR: FFmpeg not found - cannot convert to MP3")
                print(
                    "Run 'python downloader.py --setup' for "
                    "installation instructions"
                )
                return False

            ydl_opts = self._get_base_download_opts(
                clean_filename, self.config.audio_path
            )
            ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": self.config.mp3_quality,
                        }
                    ],
                }
            )

            success = self._download_with_opts(url, ydl_opts, "MP3 audio")

            if success and os.path.exists(mp3_file):
                file_size = os.path.getsize(mp3_file) / (1024 * 1024)
                print(f"MP3 completed: {mp3_file} ({file_size:.1f}MB)")
            else:
                print(f"Warning: Expected file not found: {mp3_file}")
                success = False

            return success

        except (OSError, IOError) as e:
            self.logger.error("Error in download_mp3: %s", e, exc_info=True)
            return False

    def _handle_download_error(
        self, error: yt_dlp.DownloadError, file_type: str, url: str
    ) -> None:
        """Handle download errors with specific messages."""
        error_msg = str(error)
        self.logger.error("Failed to download %s for %s: %s", file_type, url, error_msg)

        error_responses = {
            "Requested format is not available": lambda: None,
            "HTTP Error 403": "ERROR: Access denied or rate limited. Try again later.",
            "HTTP Error 429": "ERROR: Access denied or rate limited. Try again later.",
            "Video unavailable": "ERROR: Video is unavailable, private, or deleted",
        }

        for key, response in error_responses.items():
            if key in error_msg:
                if callable(response):
                    response()
                    raise FormatNotAvailableError(
                        f"Format not available: {error_msg}"
                    ) from error
                print(response)
                return

        print(f"ERROR downloading {file_type}: {error_msg}")

    def _download_with_opts(self, url: str, ydl_opts: dict, file_type: str) -> bool:
        """Generic download method with yt-dlp options."""
        if not url or not ydl_opts:
            raise ValueError("URL and download options are required")

        try:
            print(f"Downloading {file_type}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                if result != 0:
                    raise DownloadError(f"Download failed with code {result}")
            return True

        except yt_dlp.DownloadError as e:
            self._handle_download_error(e, file_type, url)
            return False

        except KeyboardInterrupt:
            print("\nDownload interrupted by user")
            self.logger.info("Download interrupted for %s", url)
            raise

        except (OSError, IOError) as e:
            print(f"ERROR: File system error downloading {file_type}: {e}")
            self.logger.error(
                "File system error downloading %s for %s: %s",
                file_type,
                url,
                e,
                exc_info=True,
            )
            return False

    def _read_urls_from_file(self, filepath: str) -> List[str]:
        """Read and validate URLs from file."""
        urls = []

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if self.validate_url(line):
                    urls.append(line)
                else:
                    print(f"Warning: Invalid URL on line {line_num}: {line}")
                    self.logger.warning("Invalid URL on line %d: %s", line_num, line)

        return urls

    def process_url(self, url: str) -> bool:
        """Process and download from a single video URL."""
        if not self.validate_url(url):
            print(f"ERROR: Not a valid URL - {url}")
            self.logger.warning("Invalid URL attempted: %s", url)
            return False

        print(f"Processing: {url}")
        return self.download_video_and_audio(url)

    def _handle_file_read_error(self, filepath: str, error: Exception) -> None:
        """Handle file reading errors."""
        error_handlers = {
            UnicodeDecodeError: (
                "ERROR: Could not read file - encoding issue. " "Try saving as UTF-8."
            ),
            PermissionError: (
                f"ERROR: Permission denied reading {filepath}. "
                f"Check file permissions."
            ),
        }

        error_type = type(error)
        if error_type in error_handlers:
            print(error_handlers[error_type])
        else:
            print(f"ERROR: Could not read {filepath}: {error}")

        self.logger.error("Failed to read URL file %s: %s", filepath, error)

    def process_url_file(self, filepath: str) -> None:
        """Process multiple URLs from a text file."""
        if not os.path.exists(filepath):
            print(f"File {filepath} not found")
            self._show_usage_help()
            return

        try:
            urls = self._read_urls_from_file(filepath)
        except (UnicodeDecodeError, PermissionError, OSError, IOError) as e:
            self._handle_file_read_error(filepath, e)
            return

        if not urls:
            print(f"No valid URLs found in {filepath}")
            return

        self._process_url_batch(urls, filepath)

    def _process_url_batch(self, urls: List[str], source: str) -> None:
        """Process a batch of URLs."""
        print(f"Found {len(urls)} URL(s) in {source}")

        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(urls)}] Starting download...")
            print(f"{'='*60}")

            if self.process_url(url):
                successful += 1
            else:
                failed += 1

        self._print_batch_summary(successful, failed, len(urls))

    def _print_batch_summary(self, successful: int, failed: int, total: int) -> None:
        """Print batch processing summary."""
        print(f"\n{'='*60}")
        print("Batch Processing Summary:")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Total: {total}")
        print(f"{'='*60}")

    def _show_usage_help(self) -> None:
        """Display basic usage help."""
        print(
            f"""
Usage:
  1. Create '{self.config.url_file}' with video URLs (one per line)
  2. Run: python downloader.py

Or download single URL:
  python downloader.py <URL>

For more options:
  python downloader.py --help
"""
        )

    def show_help(self) -> None:
        """Display comprehensive help information."""
        print(
            f"""
{'='*70}
VIDEO DOWNLOADER - HELP
{'='*70}

USAGE:
  python downloader.py                    Download from {self.config.url_file}
  python downloader.py <URL>              Download single video
  python downloader.py --formats <URL>    Show available formats
  python downloader.py --setup            Show FFmpeg setup guide
  python downloader.py --help             Show this help

SUPPORTED PLATFORMS:
  - YouTube (videos and playlists)
  - Facebook (public videos)

CONFIGURATION:
  Edit the DownloadConfig class to customize settings

OUTPUT:
  Videos saved to: {self.config.video_path}/
  Audio saved to:  {self.config.audio_path}/
  Format: [Video Title].mp4 and [Video Title].mp3

REQUIREMENTS:
  - Python 3.7+
  - yt-dlp (pip install yt-dlp)
  - FFmpeg (for MP3 conversion)

NOTES:
  - Facebook videos may require authentication for private content
  - Some videos may be restricted by region or availability
{'='*70}
"""
        )


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================


class CommandLineInterface:
    """Handle command line arguments and user interaction."""

    def __init__(self):
        """Initialize CLI with downloader instance."""
        self.downloader = YouTubeDownloader()

    def run(self, args: List[str]) -> None:
        """Run the CLI with given arguments. Added to satisfy pylint."""
        self.handle_command(args)

    def handle_command(self, args: List[str]) -> None:
        """Handle command line arguments."""
        if not args:
            self.downloader.process_url_file(self.downloader.config.url_file)
            return

        command = args[0].lower()

        command_handlers = {
            "--help": self.downloader.show_help,
            "--setup": self.downloader.show_ffmpeg_setup_help,
            "--formats": lambda: self._handle_formats(args),
        }

        if command in command_handlers:
            command_handlers[command]()
        elif self._is_url(args[0]):
            self._handle_url(args[0])
        else:
            self._handle_unknown_command(args[0])

    def _is_url(self, arg: str) -> bool:
        """Check if argument is a URL."""
        return arg.startswith(("http://", "https://"))

    def _handle_formats(self, args: List[str]) -> None:
        """Handle --formats command."""
        if len(args) < 2:
            print("ERROR: --formats requires a URL")
            print("Usage: python downloader.py --formats <URL>")
            return

        url = args[1]
        if not self.downloader.validate_url(url):
            print(f"ERROR: Invalid URL: {url}")
            return

        print(f"Available formats for: {url}\n")
        self.downloader.show_available_formats(url)

    def _handle_url(self, url: str) -> None:
        """Handle single URL download."""
        print("Processing URL from command line argument")
        print(f"Using video quality: {self.downloader.config.video_quality}\n")
        self.downloader.process_url(url)

    def _handle_unknown_command(self, command: str) -> None:
        """Handle unknown command."""
        print(
            f"""ERROR: Unknown command: {command}

Available commands:
  --help              Show help information
  --setup             Show FFmpeg setup instructions
  --formats <URL>     Show available video formats
  <URL>               Download from video URL

For more information, run: python downloader.py --help
"""
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main() -> None:
    """Main entry point for the script."""
    try:
        print("\n" + "=" * 70)
        print("VIDEO DOWNLOADER - MP4 Video & MP3 Audio")
        print("=" * 70 + "\n")

        cli = CommandLineInterface()
        cli.handle_command(sys.argv[1:])

        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except (OSError, IOError, ValueError) as e:
        print(f"\nFATAL ERROR: {e}")
        logging.error("Fatal error in main: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
