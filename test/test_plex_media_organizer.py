import sys
sys.path.append('../src/')

from plex_media_organizer import format_movie_name, guess_title

# Test format_movie_name
filename ='Avengers.Endgame.2019.mkv'
formatted_name = format_movie_name(filename)
print(formatted_name)  # Output: Avengers: Endgame (2019)

# Test format_movie_name
filename ='The.Hangover.YIFY.mkv'
formatted_name = format_movie_name(filename)
print(formatted_name)  # Output: Avengers: Endgame (2019)

# Test guess_title
title = 'The Avengers'
guessed_title = guess_title(title)
print(guessed_title)  # Output: The Avengers (2012)

