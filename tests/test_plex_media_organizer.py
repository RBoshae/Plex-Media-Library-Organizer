import os
import pytest
import sys
from typing import Dict

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(src_dir)

from plex_media_organizer import PlexMovieOrganizer 
from keys import OMDB_API_KEY

@pytest.fixture(scope='module')
def api_key():
    return OMDB_API_KEY

@pytest.fixture(scope='module')
def plex_movie_organizer(api_key):
    return PlexMovieOrganizer(api_key=api_key)

@pytest.fixture
def test_dir(tmpdir):
    # create test files and directory structure
    movies_dir = tmpdir.mkdir("movies")
    test_movie_dir = movies_dir.mkdir("Avengers")
    test_movie_dir.join("avengers.endgame.mov").write("")
    yield movies_dir

def test_format_movie_name(plex_movie_organizer):
    filename ='Avengers.Endgame.2019.mkv'
    formatted_name = plex_movie_organizer.format_movie_name(filename)
    assert formatted_name == "Avengers: Endgame (2019) (tt4154796)"

def test_plan_filepath_change(test_dir, plex_movie_organizer):
    test_movie_path = str(test_dir.join("Avengers", "avengers.endgame.mov"))
    planned_change = plex_movie_organizer.plan_filepath_change(test_movie_path)

    expected_new_path = str(test_dir.join("Avengers: Endgame (2019)", "Avengers: Endgame (2019).mov"))

    assert planned_change == (test_movie_path, expected_new_path)

def test_execute_filepath_changes(test_dir, plex_movie_organizer):
    test_movie_path = str(test_dir.join("Avengers", "avengers.endgame.mov"))

    planned_changes: Dict[str, str] = {
        test_movie_path: str(test_dir.join("Avengers: Endgame (2019)", "Avengers: Endgame (2019).mov"))
    }

    plex_movie_organizer.execute_filepath_changes(planned_changes)

    # Check if the original file no longer exists
    assert not os.path.exists(test_movie_path)

    # Check if the new file exists with the correct path
    assert os.path.exists(planned_changes[test_movie_path])