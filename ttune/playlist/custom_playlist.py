"""Temporary user-created custom playlist manager."""

from typing import List, Optional

from ttune.playlist.metadata import TrackMetadata, get_metadata


class CustomPlaylistManager:
    """Manages an in-memory temporary custom playlist created by the user."""

    def __init__(self):
        self._tracks: List[str] = []

    @property
    def tracks(self) -> List[str]:
        return list(self._tracks)

    @property
    def count(self) -> int:
        return len(self._tracks)

    def add(self, path: str) -> bool:
        """Add a track to the custom playlist if not already present."""
        if path not in self._tracks:
            self._tracks.append(path)
            return True
        return False

    def add_many(self, paths: List[str]) -> int:
        """Add multiple tracks."""
        added = 0
        for p in paths:
            if self.add(p):
                added += 1
        return added

    def remove(self, index: int) -> Optional[str]:
        """Remove track at given index."""
        if 0 <= index < len(self._tracks):
            return self._tracks.pop(index)
        return None

    def move_up(self, index: int) -> bool:
        """Move track up in playlist order."""
        if index > 0 and index < len(self._tracks):
            self._tracks[index - 1], self._tracks[index] = self._tracks[index], self._tracks[index - 1]
            return True
        return False

    def move_down(self, index: int) -> bool:
        """Move track down in playlist order."""
        if 0 <= index < len(self._tracks) - 1:
            self._tracks[index], self._tracks[index + 1] = self._tracks[index + 1], self._tracks[index]
            return True
        return False

    def clear(self):
        """Clear all tracks from the temporary playlist."""
        self._tracks.clear()


# Global singleton custom playlist shared across screens
global_custom_playlist = CustomPlaylistManager()
