
<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ManoGuzman/youtube-downloader">
    <img src="https://img.icons8.com/?size=100&id=ZUWq1ksl_Dze&format=png&color=000000" alt="YT Logo" width="80" height="80">
  </a>

<h3 align="center">YT Downloader Audio & Video</h3>

  <p align="center">
    A Python CLI tool to download YouTube and Facebook videos as MP4 or extract audio as MP3 — with quality selection, batch processing, and real-time progress.
    <br />
    <a href="https://github.com/ManoGuzman/youtube-downloader"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ManoGuzman/youtube-downloader/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ManoGuzman/youtube-downloader/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**YT Downloader** (`vdl`) is a command-line tool that downloads YouTube and Facebook videos. Given one or more video URLs (directly or via a text file), it can:

- Download videos as **MP4** with configurable quality (`best`, `worst`, or a specific resolution like `720p`)
- Extract and download audio as **MP3** using FFmpeg post-processing
- Save files to `downloads/video/` and `downloads/audio/` with clean, sanitized titles
- Skip already-downloaded files (idempotent)
- **Batch process** from a `urls.txt` file (one URL per line; `#` comments ignored)
- Validate URLs against YouTube and Facebook patterns before downloading
- Show real-time progress: percent, speed, and ETA

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python-badge]][Python-url]
* [![yt-dlp][ytdlp-badge]][ytdlp-url]
* [![FFmpeg][FFmpeg-badge]][FFmpeg-url]
* [![Typer][Typer-badge]][Typer-url]
* [![pytest][pytest-badge]][pytest-url]
* [![Ruff][Ruff-badge]][Ruff-url]
* [![GitHub Actions][GHA-badge]][GHA-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

- **Python 3.10+**
- **FFmpeg** — required for MP3 audio extraction

  To check if FFmpeg is installed:
  ```sh
  ffmpeg -version
  ```

  To see installation instructions from the CLI:
  ```sh
  vdl --setup
  ```

  Or install manually:
  - **Windows:** `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - **macOS:** `brew install ffmpeg`
  - **Linux:** `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora)

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/ManoGuzman/youtube-downloader.git
   cd youtube-downloader
   ```

2. Install the package (editable mode recommended for development)
   ```sh
   pip install -e .
   ```

3. Verify the CLI is available
   ```sh
   vdl --help
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Download a single video (best quality MP4)
```sh
vdl https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Download audio only as MP3
```sh
vdl https://www.youtube.com/watch?v=dQw4w9WgXcQ --mp3
```

### Download video only as MP4 at a specific quality
```sh
vdl https://www.youtube.com/watch?v=dQw4w9WgXcQ --mp4 --quality 720p
```

### Batch download from a file
```sh
# urls.txt — one URL per line, lines starting with # are ignored
vdl --file urls.txt
```

### Show available formats for a URL
```sh
vdl https://www.youtube.com/watch?v=dQw4w9WgXcQ --formats
```

### Custom output directory
```sh
vdl https://www.youtube.com/watch?v=dQw4w9WgXcQ --output ~/Videos
```

### CLI Reference

```
vdl [URL] [OPTIONS]

Arguments:
  URL                   Video URL to download (optional)

Options:
  -f, --file TEXT       File with URLs to download  [default: urls.txt]
  -q, --quality TEXT    Video quality: best, worst, or e.g. 720p  [default: best]
  -o, --output TEXT     Output directory  [default: downloads]
  --mp3                 Download audio only as MP3
  --mp4                 Download video only as MP4
  --formats             Show available formats for the given URL
  --setup               Show FFmpeg installation instructions
  --help                Show this message and exit.
```

> **Note:** `--mp3` and `--mp4` are mutually exclusive. If neither is specified, both video and audio are downloaded.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] YouTube video download (MP4)
- [x] Audio extraction (MP3) via FFmpeg
- [x] Facebook video support
- [x] Batch processing from `urls.txt`
- [x] Quality selection (`best`, `worst`, resolution)
- [x] Real-time progress display
- [x] Filename sanitization
- [x] GitHub Actions CI (lint, test, build)
- [ ] Playlist support
- [ ] Download subtitles / captions
- [ ] GUI / web interface
- [ ] Configurable output filename templates

See the [open issues](https://github.com/ManoGuzman/youtube-downloader/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/ManoGuzman/youtube-downloader/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ManoGuzman/youtube-downloader" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Manuel Guzman - [@LinkedIn](https://linkedin.com/in/manuel-guzmán-b87b841bb/)

Project Link: [https://github.com/ManoGuzman/youtube-downloader](https://github.com/ManoGuzman/youtube-downloader)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the core download engine powering this tool
* [FFmpeg](https://ffmpeg.org/) — for audio conversion and post-processing
* [Typer](https://typer.tiangolo.com/) — for the CLI framework
* [Rich](https://github.com/Textualize/rich) — for beautiful terminal output
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — README template
* [md-badges](https://github.com/inttter/md-badges) — badge references

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ManoGuzman/youtube-downloader.svg?style=for-the-badge
[contributors-url]: https://github.com/ManoGuzman/youtube-downloader/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ManoGuzman/youtube-downloader.svg?style=for-the-badge
[forks-url]: https://github.com/ManoGuzman/youtube-downloader/network/members
[stars-shield]: https://img.shields.io/github/stars/ManoGuzman/youtube-downloader.svg?style=for-the-badge
[stars-url]: https://github.com/ManoGuzman/youtube-downloader/stargazers
[issues-shield]: https://img.shields.io/github/issues/ManoGuzman/youtube-downloader.svg?style=for-the-badge
[issues-url]: https://github.com/ManoGuzman/youtube-downloader/issues
[license-shield]: https://img.shields.io/github/license/ManoGuzman/youtube-downloader.svg?style=for-the-badge
[license-url]: https://github.com/ManoGuzman/youtube-downloader/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/manuel-guzmán-b87b841bb/

<!-- Shields.io badges — https://github.com/inttter/md-badges -->
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=fff
[Python-url]: https://python.org/
[ytdlp-badge]: https://img.shields.io/badge/yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white
[ytdlp-url]: https://github.com/yt-dlp/yt-dlp
[FFmpeg-badge]: https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white
[FFmpeg-url]: https://ffmpeg.org/
[Typer-badge]: https://img.shields.io/badge/Typer-000000?style=for-the-badge&logo=python&logoColor=white
[Typer-url]: https://typer.tiangolo.com/
[pytest-badge]: https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white
[pytest-url]: https://pytest.org/
[Ruff-badge]: https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=000
[Ruff-url]: https://docs.astral.sh/ruff/
[GHA-badge]: https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white
[GHA-url]: https://github.com/features/actions
