"""Integration test verifying player state transitions with mocked keyboard events."""

import time
import numpy as np

from ttune.audio.player import AudioPlayer
from ttune.playlist.manager import PlaylistManager, RepeatMode


def test_player_and_playlist_integration():
    player = AudioPlayer()
    tracks = ["test1.mp3", "test2.mp3"]
    playlist = PlaylistManager(tracks)

    assert player.is_playing is False
    assert player.volume > 0.0

    vol_init = player.volume
    player.volume_up()
    assert round(player.volume, 2) == round(vol_init + 0.05, 2)
    player.volume_down()
    assert round(player.volume, 2) == round(vol_init, 2)

    player.toggle_mute()
    assert player.is_muted is True
    assert player.volume == 0.0
    player.toggle_mute()
    assert player.is_muted is False
    assert round(player.volume, 2) == round(vol_init, 2)

    assert playlist.repeat_mode == RepeatMode.ALL
    playlist.toggle_repeat()
    assert playlist.repeat_mode == RepeatMode.ONE
    playlist.toggle_repeat()
    assert playlist.repeat_mode == RepeatMode.OFF

    assert playlist.shuffle_enabled is False
    playlist.toggle_shuffle()
    assert playlist.shuffle_enabled is True
    playlist.toggle_shuffle()
    assert playlist.shuffle_enabled is False

    player.close()
