"""Tests for CustomPlaylistManager operations."""

from ttune.playlist.custom_playlist import CustomPlaylistManager


def test_custom_playlist_add_and_count():
    cpm = CustomPlaylistManager()
    assert cpm.count == 0
    assert cpm.tracks == []

    assert cpm.add("song_a.mp3") is True
    assert cpm.count == 1
    # Adding duplicate should return False and not duplicate
    assert cpm.add("song_a.mp3") is False
    assert cpm.count == 1

    assert cpm.add("song_b.mp3") is True
    assert cpm.count == 2
    assert cpm.tracks == ["song_a.mp3", "song_b.mp3"]


def test_custom_playlist_add_many():
    cpm = CustomPlaylistManager()
    added = cpm.add_many(["song1.flac", "song2.flac", "song1.flac"])
    assert added == 2
    assert cpm.count == 2


def test_custom_playlist_remove():
    cpm = CustomPlaylistManager()
    cpm.add_many(["a.mp3", "b.mp3", "c.mp3"])

    removed = cpm.remove(1)
    assert removed == "b.mp3"
    assert cpm.tracks == ["a.mp3", "c.mp3"]

    # Out of bounds
    assert cpm.remove(10) is None
    assert cpm.remove(-1) is None


def test_custom_playlist_reorder():
    cpm = CustomPlaylistManager()
    cpm.add_many(["first.mp3", "second.mp3", "third.mp3"])

    # Move down
    assert cpm.move_down(0) is True
    assert cpm.tracks == ["second.mp3", "first.mp3", "third.mp3"]
    # Cannot move down last element
    assert cpm.move_down(2) is False

    # Move up
    assert cpm.move_up(1) is True
    assert cpm.tracks == ["first.mp3", "second.mp3", "third.mp3"]
    # Cannot move up first element
    assert cpm.move_up(0) is False


def test_custom_playlist_clear():
    cpm = CustomPlaylistManager()
    cpm.add_many(["a.mp3", "b.mp3"])
    assert cpm.count == 2
    cpm.clear()
    assert cpm.count == 0
    assert cpm.tracks == []