"""Tests for MusicSearchEngine."""

from pathlib import Path
from ttune.playlist.searcher import MusicSearchEngine


def test_music_search_token_matching(tmp_path):
    d = tmp_path / "music_folder"
    d.mkdir()
    f1 = d / "Cyberpunk Synthwave 2077.mp3"
    f1.write_text("dummy")
    f2 = d / "Retro Chill Hop.flac"
    f2.write_text("dummy")
    f3 = d / "Hard Rock Anthem.wav"
    f3.write_text("dummy")

    engine = MusicSearchEngine()
    engine._roots = [d]
    engine._is_indexed = False
    engine.index_all()

    assert len(engine._cached_files) == 3

    res = engine.search("synthwave")
    assert len(res) == 1
    assert "Cyberpunk Synthwave" in res[0]

    res = engine.search("retro chill")
    assert len(res) == 1
    assert "Retro Chill" in res[0]

    res = engine.search("ROCK")
    assert len(res) == 1
    assert "Hard Rock" in res[0]

    res = engine.search("orchestral classical")
    assert len(res) == 0

    res = engine.search("")
    assert len(res) == 3