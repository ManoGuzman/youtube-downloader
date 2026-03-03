<img src="https://img.icons8.com/?size=100&id=ZUWq1ksl_Dze&format=png&color=000000" alt="YouTube Downloader Logo" align="right" width="120">

# YouTube Downloader &middot; [![Python](https://img.shields.io/badge/python-3.7+-blue.svg?style=flat-square)](https://www.python.org/downloads/) [![yt-dlp](https://img.shields.io/badge/yt--dlp-2024.12.7+-red.svg?style=flat-square)](https://github.com/yt-dlp/yt-dlp) [![License](https://img.shields.io/badge/license-Personal%20Use-green.svg?style=flat-square)](LICENSE)

> A Python-based YouTube video and audio downloader powered by yt-dlp and FFmpeg

Download YouTube videos in MP4 format and extract high-quality audio in MP3 format with automatic batch processing support.

## Installing / Getting started

Quick setup to download your first video:

```shell
# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (Windows)
winget install --id=Gyan.FFmpeg

# Download a video
python src/downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This will download both MP4 video and MP3 audio to the `downloads/` folder automatically.

## Developing

### Built With

- **Python 3.7+** - Core runtime environment
- **yt-dlp >= 2024.12.7** - YouTube downloading library (fork of youtube-dl with active maintenance)
- **FFmpeg 8.0+** - Audio/video processing and conversion

### Prerequisites

Before setting up the development environment, you need:

1. **Python 3.7 or higher** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg executables**:
   - Windows: [WinGet](https://learn.microsoft.com/en-us/windows/package-manager/winget/) or [Gyan.dev builds](https://www.gyan.dev/ffmpeg/builds/)
   - macOS: [Homebrew](https://brew.sh/)
   - Linux: System package manager
3. **Git** (optional) - For cloning the repository

### Setting up Dev

Clone and set up the project:

```shell
git clone https://github.com/your/youtube_downloader.git
cd youtube_downloader/
pip install -r requirements.txt
```

**Install FFmpeg:**

```shell
# Windows (WinGet)
winget install --id=Gyan.FFmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg
```

**Verify installation:**

```shell
ffmpeg -version
python src/downloader.py --help
```

The script will auto-create the `downloads/` directory on first run. For batch processing, create a `urls.txt` file with YouTube URLs (one per line).

### Building

This is a Python script project - no build step required. However, you can package it as an executable:

```shell
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --name youtube-downloader src/downloader.py
```

The executable will be created in `dist/youtube-downloader.exe` (Windows) or `dist/youtube-downloader` (Unix).

### Deploying / Publishing

To create a distributable package:

```shell
# Create source distribution
python setup.py sdist

# Create wheel distribution
python setup.py bdist_wheel

# Upload to PyPI (requires account)
pip install twine
twine upload dist/*
```

For standalone deployment, distribute the executable from the Building section along with FFmpeg installation instructions.

## Versioning

This project follows [Semantic Versioning](http://semver.org/). 

Current version: **1.0.0**

For available versions, see the [releases page](https://github.com/your/youtube_downloader/releases).

## Configuration

Configure download settings by editing the `DownloadConfig` class in `src/downloader.py` (lines 31-49):

### Video Quality Options

```python
video_quality: str = "best"              # Default: highest available
```

**Available settings:**
- `"best"` - Highest quality available
- `"best[height<=1080]"` - Maximum 1080p
- `"best[height<=720]"` - Maximum 720p
- `"best[height<=480]"` - Maximum 480p
- `"best[filesize<50M]"` - Maximum 50MB file size

### Audio Quality Options

```python
mp3_quality: str = "192"                 # Default: 192 kbps
```

**Available settings:**
- `"320"` - Highest quality (larger files)
- `"192"` - Balanced quality (recommended)
- `"128"` - Standard quality (smaller files)

### Output Directory

```python
output_path: str = "downloads"           # Change output location
```

### File Naming

```python
max_filename_length: int = 500           # Maximum filename length
```

### Batch Processing

Create `urls.txt` in the project root:

```txt
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
# Lines starting with # are ignored
```

Run without arguments to process the file:

```shell
python src/downloader.py
```

## Tests

Currently, this project does not include automated tests. Manual testing can be performed:

```shell
# Test single URL download
python src/downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Test format listing
python src/downloader.py --formats "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Test FFmpeg detection
python src/downloader.py --setup

# Verify log output
type downloader.log  # Windows
cat downloader.log   # Unix
```

**What these tests verify:**
- FFmpeg availability and PATH configuration
- yt-dlp video fetching capability
- MP3 audio extraction
- Filename sanitization and security
- Error handling and logging
- Duplicate file detection

## Style guide

This project follows [PEP 8](https://pep8.org/) Python style guidelines:

```shell
# Check code style
pip install flake8
flake8 src/downloader.py

# Auto-format code
pip install black
black src/downloader.py
```

**Key conventions:**
- 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Type hints using `dataclass` decorators
- Docstrings for all public functions
- Comprehensive error handling
- Security-focused filename sanitization

## API Reference

### Command Line Interface

```shell
python src/downloader.py [OPTIONS] [URL]
```

**Arguments:**
- `URL` - YouTube video URL (optional if using urls.txt)

**Options:**
- `--formats <URL>` - Display available video/audio formats for a URL
- `--help` - Show help message and current configuration
- `--setup` - Display FFmpeg installation guide

### Core Classes

**`YouTubeDownloader`**
- Main downloader class with all functionality
- Handles video/audio downloads, format selection, and file management

**`DownloadConfig`**
- Configuration dataclass for download settings
- Automatically creates output directory on initialization

**`CommandLineInterface`**
- CLI handler for processing command-line arguments

### Key Methods

**`download_video_and_audio(url: str) -> bool`**
- Downloads MP4 video and MP3 audio from YouTube URL
- Skips existing files automatically
- Returns: `True` on success, `False` on failure

**`download_mp4(url: str, clean_filename: str, mp4_file: str) -> bool`**
- Downloads video in MP4 format
- Uses format selector from configuration
- Returns: `True` on success, `False` on failure

**`download_mp3(url: str, clean_filename: str, mp3_file: str) -> bool`**
- Extracts and converts audio to MP3 format
- Requires FFmpeg to be installed
- Returns: `True` on success, `False` on failure

**`process_url_file(filepath: str) -> None`**
- Batch processes URLs from text file
- Skips comments and empty lines
- Provides summary statistics

**`clean_title(title: str) -> str`**
- Sanitizes video titles for safe filenames
- Removes path traversal attempts and invalid characters
- Enforces maximum length limits

**`validate_url(url: str) -> bool`**
- Validates YouTube URL format
- Supports standard videos, mobile URLs, and playlists

## Database

This project does not use a database. All state is file-based:

- **downloads/** - Output directory for MP4 and MP3 files
- **urls.txt** - Optional input file for batch processing
- **downloader.log** - Execution logs and error tracking

**File naming convention:** `{sanitized_video_title}.{ext}`

Files are automatically skipped if they already exist, preventing duplicate downloads.

## Licensing

**Educational and Personal Use Only**

This software is provided for educational purposes and personal use. Users must:
- Respect YouTube's Terms of Service
- Comply with copyright laws
- Not redistribute copyrighted content
- Use responsibly and ethically

See [YouTube Terms of Service](https://www.youtube.com/t/terms) for platform-specific restrictions.

---

**⚠️ Important:** This tool is designed for downloading content you have rights to access. Downloading copyrighted material without permission may be illegal in your jurisdiction.