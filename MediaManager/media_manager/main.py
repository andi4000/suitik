"""Suitik MediaManager API Endpoints"""
import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine, select
from pydantic import BaseSettings
import aiofiles

from media_manager.models import (
    ApiTags,
    CardAssignment,
    PlaylistSong,
    SongOut,
    SongCreate,
    Song,
    Playlist,
    PlaylistCreate,
)

# API Endpoints
# GET    /songs
# POST   /songs
# PATCH  /songs/{s_id}                  # only change name
# DELETE /songs/{s_id}
#
# GET    /playlists
# POST   /playlists
# PATCH  /playlists                     # only change name
# DELETE /playlists/{p_id}

# POST   /playlists/{p_id}/songs        # add song (s_id) to playlist
# GET    /playlists/{p_id}/songs
# PUT    /playlists/{p_id}/songs        # to change order ?unclear?
# DELETE /playlists/{p_id}/songs/{s_id}
#
# PUT    /cards                         # input: either s_id or p_id
# GET    /cards/{c_id}/songs            # returns array


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class Settings(BaseSettings):
    files_path_prefix: str = os.getcwd() + "/files"


settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    if not os.path.exists(settings.files_path_prefix):
        os.mkdir(settings.files_path_prefix)


@app.get("/songs/", response_model=List[SongOut], tags=[ApiTags.SONGS])
async def get_songs(sess: Session = Depends(get_session)):
    songs = sess.exec(select(Song)).all()
    return songs


@app.post("/songs/", tags=[ApiTags.SONGS])
async def create_song(file: UploadFile, sess: Session = Depends(get_session)):
    song_name, ext = os.path.splitext(file.filename)

    if not ext.lower().endswith("mp3"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="only mp3 files are supported",
        )

    db_song = Song(name=song_name)
    song_path = None

    # write to db to get ID
    sess.add(db_song)
    sess.commit()
    sess.refresh(db_song)

    song_path = f"{settings.files_path_prefix}/{db_song.id:03d}_{file.filename}"

    # TODO: handle error writing by deleting db entry
    async with aiofiles.open(song_path, "wb") as outfile:
        content = await file.read()
        await outfile.write(content)

    song_uri = f"file://{song_path}"

    db_song.uri = song_uri
    sess.add(db_song)
    sess.commit()
    sess.refresh(db_song)

    return db_song


@app.patch("/songs/{song_id}", response_model=SongOut, tags=[ApiTags.SONGS])
async def change_song(
    song_id: int, song: SongCreate, sess: Session = Depends(get_session)
):
    db_song = sess.get(Song, song_id)
    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")

    new_song = song.dict(exclude_unset=True)
    for k, v in new_song.items():
        setattr(db_song, k, v)

    sess.add(db_song)
    sess.commit()
    sess.refresh(db_song)
    return db_song


@app.delete("/songs/{song_id}", response_model=SongOut, tags=[ApiTags.SONGS])
async def delete_song(song_id: int, sess: Session = Depends(get_session)):
    db_song = sess.get(Song, song_id)
    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")
    sess.delete(db_song)
    sess.commit()
    return db_song


@app.get("/playlists/", response_model=List[Playlist], tags=[ApiTags.PLAYLISTS])
async def get_playlists(sess: Session = Depends(get_session)):
    playlists = sess.exec(select(Playlist)).all()
    return playlists


@app.post("/playlists/", response_model=Playlist, tags=[ApiTags.PLAYLISTS])
async def create_playlist(
    playlist: PlaylistCreate, sess: Session = Depends(get_session)
):
    # TODO: check if name is used?
    db_playlist = Playlist.from_orm(playlist)
    sess.add(db_playlist)
    sess.commit()
    sess.refresh(db_playlist)
    return db_playlist


@app.patch(
    "/playlists/{playlist_id}", response_model=Playlist, tags=[ApiTags.PLAYLISTS]
)
async def change_playlist(
    playlist_id: int, playlist: PlaylistCreate, sess: Session = Depends(get_session)
):
    db_playlist = sess.get(Playlist, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    new_playlist = playlist.dict(exclude_unset=True)
    for k, v in new_playlist.items():
        setattr(db_playlist, k, v)

    sess.add(db_playlist)
    sess.commit()
    sess.refresh(db_playlist)
    return db_playlist


@app.delete(
    "/playlists/{playlist_id}", response_model=Playlist, tags=[ApiTags.PLAYLISTS]
)
async def delete_playlist(playlist_id: int, sess: Session = Depends(get_session)):
    db_playlist = sess.get(Playlist, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    sess.delete(db_playlist)
    sess.commit()
    return db_playlist


# TODO: add multiple songs?
@app.post(
    "/playlists/{playlist_id}/songs", response_model=SongOut, tags=[ApiTags.PLAYLISTS]
)
def add_song_to_playlist(
    playlist_id: int, song_id: int, sess: Session = Depends(get_session)
):
    db_playlist = sess.get(Playlist, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    db_song = sess.get(Song, song_id)
    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")

    db_playlist.songs.append(db_song)
    sess.add(db_playlist)
    sess.commit()
    sess.refresh(db_song)
    return db_song


@app.get(
    "/playlists/{playlist_id}/songs",
    response_model=List[SongOut],
    tags=[ApiTags.PLAYLISTS],
)
def get_songs_from_playlist(playlist_id: int, sess: Session = Depends(get_session)):
    db_playlist = sess.get(Playlist, playlist_id)

    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    return songs_from_playlist(playlist_id, sess)


def songs_from_playlist(playlist_id: int, sess: Session) -> List[SongOut]:
    # TODO: there should be a better way to do this
    result = sess.exec(
        select(PlaylistSong).where(PlaylistSong.playlist_id == playlist_id)
    )

    songs = []
    for res in result:
        song_id = res.song_id
        songs.append(sess.get(Song, song_id))

    return songs


@app.delete(
    "/playlists/{playlist_id}/songs/{song_id}",
    response_model=SongOut,
    tags=[ApiTags.PLAYLISTS],
)
def delete_song_from_playlist(
    playlist_id: int, song_id: int, sess: Session = Depends(get_session)
):
    db_playlist = sess.get(Playlist, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    db_song = sess.get(Song, song_id)
    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")

    if db_song not in db_playlist.songs:
        raise HTTPException(status_code=404, detail="Song does not exist in playlist")

    db_playlist.songs.remove(db_song)
    sess.add(db_playlist)
    sess.commit()
    sess.refresh(db_song)
    return db_song


@app.get("/cards/{card_id}/songs", response_model=List[SongOut], tags=[ApiTags.CARDS])
async def get_songs_from_card(card_id: str, sess: Session = Depends(get_session)):
    db_card = sess.get(CardAssignment, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")

    if db_card.playlist_id:
        return songs_from_playlist(db_card.playlist_id, sess)

    if db_card.song_id:
        db_song = sess.get(Song, db_card.song_id)
        if not db_song:
            raise HTTPException(status_code=404, detail="Song not found")

        return [db_song]


@app.put("/cards", response_model=CardAssignment, tags=[ApiTags.CARDS])
async def assign_card(
    assignment: CardAssignment, response: Response, sess: Session = Depends(get_session)
):
    # TODO: maybe validate in model?
    if (assignment.playlist_id is None and assignment.song_id is None) or (
        assignment.playlist_id is not None and assignment.song_id is not None
    ):
        raise HTTPException(
            status_code=400, detail="Card can only trigger either a song or a playlist"
        )

    if assignment.song_id:
        db_song = sess.get(Song, assignment.song_id)
        if not db_song:
            raise HTTPException(status_code=404, detail="Song not found")

    if assignment.playlist_id:
        db_playlist = sess.get(Playlist, assignment.playlist_id)
        if not db_playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

    db_card_assignment = sess.get(CardAssignment, assignment.card_id)

    if db_card_assignment:
        updated_assignment = assignment.dict()
        for k, v in updated_assignment.items():
            setattr(db_card_assignment, k, v)

        sess.add(db_card_assignment)
        sess.commit()
        sess.refresh(db_card_assignment)
        response.status_code = 200
        return db_card_assignment
    else:
        new_assignment = CardAssignment.from_orm(assignment)
        sess.add(new_assignment)
        sess.commit()
        sess.refresh(new_assignment)
        response.status_code = 201
        return new_assignment
