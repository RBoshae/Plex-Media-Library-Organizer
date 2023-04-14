import pytest
import sys
sys.path.append('../src')

from plex_media_organizer import PlexMediaOrganizer 

@pytest.fixture
def test_dir(tmpdir):
    # create test files and directory structure
    movies_dir = tmpdir.mkdir("movies")
    test_movie_dir = movies_dir.mkdir("Avengers")
    test_movie_dir.join("avengers.endgame.mov").write("")
    yield movies_dir

def test_rename_and_move_movie(test_dir):
    organizer = PlexMediaOrganizer()

    # get the path to the test movie file
    test_movie_path = test_dir.join("Avengers", "avengers.mov")

    # run the method on the test movie file
    organizer.rename_and_move_movie(test_movie_path)

    # check if the file and directory were named correctly
    assert not test_movie_path.exists()
    assert test_dir.join("Avengers: Endgame (2019)").join("Avengers: Endgame (2019).mov").exists()

# Test format_movie_name
def test_format_movie_name():
    organizer = PlexMediaOrganizer()
    filename ='Avengers.Endgame.2019.mkv'
    formatted_name = organizer.format_movie_name(filename)
    assert formatted_name == "Avengers: Endgame (2019)"

# Test guess_title
def test_guess_movie_title():
    organizer = PlexMediaOrganizer()
    title = 'The Avengers'
    guessed_title = organizer.guess_movie_title(title)
    assert guessed_title == "Avengers: Endgame (2019)"

