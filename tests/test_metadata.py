"""Tests for metadata formatting and extraction."""

from ttune.playlist.metadata import clean_filename, format_duration, get_metadata


def test_format_duration():
    assert format_duration(0) == "00:00"
    assert format_duration(65) == "01:05"
    assert format_duration(3599) == "59:59"
    assert format_duration(3600) == "01:00:00"
    assert format_duration(3665) == "01:01:05"


def test_clean_filename():
    assert clean_filename("01 - Cyberpunk Dreams (Official Music Video).mp3") == "Cyberpunk Dreams"
    assert clean_filename("Artist - Track (Lyrics) [TubeRipper.com].m4a") == "Artist - Track"
    assert clean_filename("NebulaVex Song (MP3_160K).mp3") == "NebulaVex Song"
    assert clean_filename("simple_song_name.mp3") == "simple song name"


def test_get_metadata_fallback_nonexistent():
    meta = get_metadata("nonexistent_song_artist - title.mp3")
    assert meta.title == "title"
    assert meta.artist == "nonexistent_song_artist"
    assert meta.format_name == "MP3"
