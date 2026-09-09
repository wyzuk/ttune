"""Tests for PlaylistManager operations, shuffle, and repeat modes."""

from ttune.playlist.manager import PlaylistManager, RepeatMode


def test_playlist_navigation():
    tracks = ["song1.mp3", "song2.mp3", "song3.mp3"]
    pm = PlaylistManager(tracks)

    assert pm.count == 3
    assert pm.current_path() == "song1.mp3"

    next_t = pm.next_track()
    assert pm.current_path() == "song2.mp3"

    next_t = pm.next_track()
    assert pm.current_path() == "song3.mp3"

    next_t = pm.next_track()
    assert pm.current_path() == "song1.mp3"

    prev_t = pm.prev_track()
    assert pm.current_path() == "song3.mp3"


def test_repeat_modes():
    tracks = ["song1.mp3", "song2.mp3"]
    pm = PlaylistManager(tracks)

    assert pm.repeat_mode == RepeatMode.ALL
    pm.toggle_repeat()
    assert pm.repeat_mode == RepeatMode.ONE

    curr = pm.next_track(force=False)
    assert pm.current_path() == "song1.mp3"

    curr = pm.next_track(force=True)
    assert pm.current_path() == "song2.mp3"

    pm.toggle_repeat()
    assert pm.repeat_mode == RepeatMode.OFF

    assert pm.next_track() is None


def test_up_next_list():
    tracks = ["song1.mp3", "song2.mp3", "song3.mp3", "song4.mp3"]
    pm = PlaylistManager(tracks)

    up_next = pm.get_up_next(count=2)
    assert len(up_next) == 2
    assert up_next[0].filename == "song2.mp3"
    assert up_next[1].filename == "song3.mp3"
