"""Command-line interface for the video downloader."""

from pathlib import Path
from typing import Optional

import typer

from vdl.downloader import DownloadConfig, YouTubeDownloader

app = typer.Typer(
    name="vdl",
    help="Download YouTube and Facebook videos as MP4 and MP3",
)


@app.command()
def main(
    url: Optional[str] = typer.Argument(None, help="Video URL to download"),
    url_file: str = typer.Option(
        "urls.txt", "--file", "-f", help="File containing URLs to download"
    ),
    quality: str = typer.Option(
        "best",
        "--quality",
        "-q",
        help="Video quality (best, worst, or specific resolution like 720p)",
    ),
    output: str = typer.Option("downloads", "--output", "-o", help="Output directory"),
    mp3_only: bool = typer.Option(False, "--mp3", help="Download audio only as MP3"),
    mp4_only: bool = typer.Option(False, "--mp4", help="Download video only as MP4"),
    show_formats: bool = typer.Option(
        False, "--formats", help="Show available formats for URL"
    ),
    setup: bool = typer.Option(False, "--setup", help="Show FFmpeg setup instructions"),
) -> None:
    if mp3_only and mp4_only:
        typer.echo("ERROR: Cannot use both --mp3 and --mp4", err=True)
        raise typer.Exit(1)

    config = DownloadConfig(
        output_path=output,
        video_quality=quality,
    )
    downloader = YouTubeDownloader(config)

    if setup:
        downloader.show_ffmpeg_setup_help()
        return

    if show_formats:
        if not url:
            typer.echo("ERROR: --formats requires a URL", err=True)
            raise typer.Exit(1)
        downloader.show_available_formats(url)
        return

    try:
        if url:
            downloader.process_url(url)
        elif Path(url_file).exists():
            downloader.process_url_file(url_file)
        else:
            typer.echo(f"ERROR: URL file not found: {url_file}", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
