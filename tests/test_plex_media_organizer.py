import os
import pytest
import shutil
import sys
from pathlib import Path
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
def movies_tmpdir(tmpdir, request):
    # Creating a unique subdirectory for each test
    movies_dir = tmpdir.mkdir(request.node.name)
    return movies_dir
    

@pytest.fixture
def simple_movie_path_structure(movies_tmpdir):
    # create test files and directory structure
    movies_dir = movies_tmpdir.mkdir("movies")
    test_movie_dir = movies_dir.mkdir("Avengers")
    test_movie_dir.join("avengers.endgame.mov").write("")
    yield movies_dir

    
@pytest.fixture()
def expected_simple(movies_tmpdir):
    # Return the expected result for the simple case
    movies_path = str(movies_tmpdir)
    return { 
            f'{movies_path}/movies/Avengers/avengers.endgame.mov' : f'{movies_path}/movies/Avengers Endgame (2019)/Avengers Endgame (2019) (tt4154796).mov'
    }
    

@pytest.fixture
def large_movie_path_structure(movies_tmpdir):
    movies_dir = movies_tmpdir.mkdir("movies")
    
    # Avengers
    avengers = movies_dir.mkdir("Avengers")
    avengers.join("avengers.endgame.mov").write("")
    avengers.join("poster.jpeg").write("")
    avengers.join("avengers.endgame.srt").write("")
    
    # Inception
    inception = movies_dir.mkdir("Inception")
    inception.join("inception.mkv").write("")
    inception.join("poster.jpeg").write("")
    inception.join("inception.srt").write("")
    
    # Interstellar
    interstellar = movies_dir.mkdir("Interstellar")
    interstellar.join("interstellar.mkv").write("")
    interstellar.join("poster.jpeg").write("")
    interstellar.join("interstellar.srt").write("")
    
    # Toy Story
    toy_story = movies_dir.mkdir("Toy_Story")
    toy_story.join("toy_story.mp4").write("")
    toy_story.join("poster.jpeg").write("")
    toy_story.join("toy_story.srt").write("")
    
    yield str(movies_dir)

    # Cleanup
    shutil.rmtree(movies_dir)


@pytest.fixture()
def expected_large(movies_tmpdir):
    movies_path = str(movies_tmpdir)
    return {
        f'{movies_path}/movies/Avengers/avengers.endgame.mov': f'{movies_path}/movies/Avengers Endgame (2019).mov',
        f'{movies_path}/movies/Inception/inception.mkv': f'{movies_path}/movies/Inception (2010).mkv',
        f'{movies_path}/movies/Interstellar/interstellar.mkv': f'{movies_path}/movies/Interstellar (2014).mkv',
        f'{movies_path}/movies/Toy_Story/toy_story.mp4': f'{movies_path}/movies/Toy Story (1995).mp4',
    } 

def test_format_movie_filename(plex_movie_organizer):
    # Sample movie data
    movie_data = {
        "Title": "The Shawshank Redemption",
        "Year": "1994",
        "imdbID": "tt0111161"
    }

    # Expected formatted movie filename
    expected_filename = "The Shawshank Redemption (1994) (tt0111161)"

    # Call the format_movie_filename function
    formatted_filename = plex_movie_organizer.format_movie_filename(movie_data)

    # Assert that the output matches the expected result
    assert formatted_filename == expected_filename

@pytest.mark.parametrize("movie_path, expected", [
    ("simple_movie_path_structure", "expected_simple"), 
    ("large_movie_path_structure", "expected_large")
])
def test_plan_changes(movie_path, expected, plex_movie_organizer, request):
    
    test_movie_path = str(request.getfixturevalue(movie_path))
    planned_changes = plex_movie_organizer.plan_changes(test_movie_path,
                                                       recursive=True)

    expected_plans = request.getfixturevalue(expected) 

    assert planned_changes == expected_plans

def test_execute_filepath_changes(tmpdir, plex_movie_organizer):
    test_movie_path = str(tmpdir.join("Avengers", "avengers.endgame.mov"))

    planned_changes: Dict[str, str] = {
        test_movie_path: str(tmpdir.join("Avengers Endgame (2019)", "Avengers Endgame (2019).mov"))
    }

    plex_movie_organizer.execute_filepath_changes(planned_changes)

    # Check if the original file no longer exists
    assert not os.path.exists(test_movie_path)

    # Check if the new file exists with the correct path
    assert os.path.exists(planned_changes[test_movie_path])