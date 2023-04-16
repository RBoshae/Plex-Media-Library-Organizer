import os
import pytest
import sys

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(src_dir)

from plex_media_organizer import PlexMediaOrganizer 
from keys import OMDB_API_KEY

@pytest.fixture(scope='module')
def api_key():
    return OMDB_API_KEY

@pytest.fixture(scope='module')
def plex_media_organizer(api_key):
    return PlexMediaOrganizer(api_key=api_key)

@pytest.fixture
def test_dir(tmpdir):
    # create test files and directory structure
    movies_dir = tmpdir.mkdir("movies")
    test_movie_dir = movies_dir.mkdir("Avengers")
    test_movie_dir.join("avengers.endgame.mov").write("")
    yield movies_dir

def test_format_movie_name(plex_media_organizer):
    filename ='Avengers.Endgame.2019.mkv'
    formatted_name = plex_media_organizer.format_movie_name(filename)
    assert formatted_name == "Avengers: Endgame (2019) (tt4154796)"

def test_rename_and_move_movie(test_dir, plex_media_organizer):
    # get the path to the test movie file
    test_movie_path = test_dir.join("Avengers", "avengers.mov")

    # run the method on the test movie file
    plex_media_organizer.rename_and_move_movie(test_movie_path)

    # check if the file and directory were named correctly
    assert not test_movie_path.exists()
    assert test_dir.join("Avengers: Endgame (2019)").join("Avengers: Endgame (2019).mov").exists()