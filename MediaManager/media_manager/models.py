from enum import Enum
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class PlaylistSong(SQLModel, table=True):
    """Holds songs in playlist"""

    playlist_id: Optional[int] = Field(
        default=None, foreign_key="playlist.id", primary_key=True
    )
    song_id: Optional[int] = Field(
        default=None, foreign_key="song.id", primary_key=True
    )


class PlaylistBase(SQLModel):
    name: str = Field(index=True)


class Playlist(PlaylistBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    songs: List["Song"] = Relationship(
        back_populates="playlists", link_model=PlaylistSong
    )


class PlaylistCreate(PlaylistBase):
    pass


class SongBase(SQLModel):
    name: str = Field(index=True)


class Song(SongBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uri: Optional[str] = None
    playlists: List[Playlist] = Relationship(
        back_populates="songs", link_model=PlaylistSong
    )


class SongCreate(SongBase):
    pass


class SongOut(SongBase):
    id: int
    uri: Optional[str]


class CardAssignment(SQLModel, table=True):
    """One card can have either `playlist_id`, or `song_id`, not both."""

    card_id: str = Field(default=None, primary_key=True)
    playlist_id: Optional[int] = Field(
        default=None, foreign_key="playlist.id", primary_key=True
    )
    song_id: Optional[int] = Field(
        default=None, foreign_key="song.id", primary_key=True
    )


class ApiTags(Enum):
    CARDS = "cards"
    SONGS = "songs"
    PLAYLISTS = "playlists"
