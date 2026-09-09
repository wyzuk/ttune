"""Playlist and queue management with shuffle, repeat, and fast navigation."""

import random
from enum import Enum
from typing import Dict, List, Optional

from ttune.playlist.metadata import TrackMetadata, get_metadata


class RepeatMode(Enum):
    OFF = "OFF"
    ALL = "ALL"
    ONE = "ONE"


class PlaylistManager:
    """Manages the queue of tracks, navigation, shuffle, and repeat modes."""

    def __init__(self, track_paths: Optional[List[str]] = None):
        self._original_tracks: List[str] = list(track_paths) if track_paths else []
        self._tracks: List[str] = list(self._original_tracks)
        self._current_index: int = 0
        self._repeat_mode: RepeatMode = RepeatMode.ALL
        self._shuffle: bool = False
        self._meta_cache: Dict[str, TrackMetadata] = {}

    @property
    def tracks(self) -> List[str]:
        return self._tracks

    @property
    def count(self) -> int:
        return len(self._tracks)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def repeat_mode(self) -> RepeatMode:
        return self._repeat_mode

    @property
    def shuffle_enabled(self) -> bool:
        return self._shuffle

    def set_tracks(self, paths: List[str], start_index: int = 0):
        """Set a new list of tracks and reset index."""
        self._original_tracks = list(paths)
        self._tracks = list(paths)
        self._current_index = max(0, min(start_index, len(self._tracks) - 1)) if self._tracks else 0
        if self._shuffle:
            self._apply_shuffle()

    def get_track_metadata(self, index: int) -> Optional[TrackMetadata]:
        """Get metadata for track at index (cached)."""
        if 0 <= index < len(self._tracks):
            path = self._tracks[index]
            if path not in self._meta_cache:
                self._meta_cache[path] = get_metadata(path)
            return self._meta_cache[path]
        return None

    def current_track(self) -> Optional[TrackMetadata]:
        """Get metadata for the currently active track."""
        return self.get_track_metadata(self._current_index)

    def current_path(self) -> Optional[str]:
        """Get path of current track."""
        if 0 <= self._current_index < len(self._tracks):
            return self._tracks[self._current_index]
        return None

    def next_track(self, force: bool = False) -> Optional[TrackMetadata]:
        """Advance to the next track according to repeat and shuffle rules.

        Args:
            force: If True (e.g. user pressed next key), ignore RepeatMode.ONE
                   and move to next song.
        """
        if not self._tracks:
            return None

        if self._repeat_mode == RepeatMode.ONE and not force:
            return self.current_track()

        if self._current_index + 1 < len(self._tracks):
            self._current_index += 1
            return self.current_track()
        elif self._repeat_mode == RepeatMode.ALL or self._shuffle:
            self._current_index = 0
            return self.current_track()
        else:
            return None

    def prev_track(self) -> Optional[TrackMetadata]:
        """Move to previous track."""
        if not self._tracks:
            return None

        if self._current_index > 0:
            self._current_index -= 1
        elif self._repeat_mode == RepeatMode.ALL or self._shuffle:
            self._current_index = len(self._tracks) - 1
        return self.current_track()

    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode and reorder queue while preserving current song."""
        if not self._tracks:
            self._shuffle = not self._shuffle
            return self._shuffle

        curr_path = self.current_path()
        self._shuffle = not self._shuffle

        if self._shuffle:
            self._apply_shuffle(curr_path)
        else:
            # Revert to original order
            self._tracks = list(self._original_tracks)
            if curr_path and curr_path in self._tracks:
                self._current_index = self._tracks.index(curr_path)

        return self._shuffle

    def _apply_shuffle(self, current_path_to_keep: Optional[str] = None):
        """Shuffle remaining items, keeping current item at current position."""
        if len(self._tracks) <= 1:
            return

        curr = current_path_to_keep or self.current_path()
        remaining = [p for p in self._original_tracks if p != curr]
        random.shuffle(remaining)
        if curr:
            self._tracks = [curr] + remaining
            self._current_index = 0
        else:
            self._tracks = remaining
            self._current_index = 0

    def toggle_repeat(self) -> RepeatMode:
        """Cycle repeat mode: ALL -> ONE -> OFF -> ALL."""
        modes = [RepeatMode.ALL, RepeatMode.ONE, RepeatMode.OFF]
        curr_idx = modes.index(self._repeat_mode)
        self._repeat_mode = modes[(curr_idx + 1) % len(modes)]
        return self._repeat_mode

    def get_up_next(self, count: int = 5) -> List[TrackMetadata]:
        """Get the next N upcoming tracks for the UP NEXT display."""
        if not self._tracks or len(self._tracks) <= 1:
            return []

        results: List[TrackMetadata] = []
        num_tracks = len(self._tracks)

        for i in range(1, count + 1):
            next_idx = (self._current_index + i)
            if next_idx >= num_tracks:
                if self._repeat_mode == RepeatMode.ALL or self._shuffle:
                    next_idx = next_idx % num_tracks
                else:
                    break
            meta = self.get_track_metadata(next_idx)
            if meta:
                results.append(meta)

        return results
