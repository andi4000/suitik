from enum import Enum
from typing import List, Optional

from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship


class SpecialPlaybackMode(str, Enum):
    SHUFFLE_ALL_ONCE = "shuffle_all_once"
    LATEST_10 = "latest_10"
    LATEST_20 = "latest_20"


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

    # When assigned playlist or song is deleted, CardAssignment entry should
    # also be deleted.
    # Ref: https://github.com/tiangolo/sqlmodel/issues/213#issuecomment-1133170226
    assigned_cards: List["CardAssignment"] = Relationship(
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
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

    assigned_cards: List["CardAssignment"] = Relationship(
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )


class SongCreate(SongBase):
    pass


class SongOut(SongBase):
    id: int
    uri: Optional[str]


class CardAssignment(SQLModel, table=True):
    """One card can have either `playlist_id`, or `song_id`, not both."""

    playlist_id: Optional[int] = Field(default=None, foreign_key="playlist.id")
    song_id: Optional[int] = Field(default=None, foreign_key="song.id")
    special_playback: Optional[SpecialPlaybackMode] = Field(default=None)

    card_id: str = Field(default=None, primary_key=True)

    @validator("card_id")
    def card_validator(cls, val, values, **kwargs):
        if len([k for k, v in values.items() if v is not None]) > 1:
            raise ValueError("Only one type can be assigned to a card.")
        return val


class ApiTags(Enum):
    CARDS = "cards"
    SONGS = "songs"
    PLAYLISTS = "playlists"
    SPECIAL = "special"
