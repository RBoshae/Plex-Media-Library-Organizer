import json
import os
import requests
import re

from typing import Optional

from config import COMMON_STRINGS_FILE


class PlexMediaOrganizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Creates an instance of the PlexMediaOrganizer class.

        :param api_key: (Optional) The API key to use for requests to the OMDb API. If not provided, it will look for the
                        key in the environment variable "OMDB_API_KEY". If not found there, it will try to import the key
                        from a module named "keys" in the current working directory.
        """

        if api_key is None:
            api_key = os.environ.get('OMDB_API_KEY') or keys.OMDB_API_KEY
        self.api_key = api_key

    def format_movie_name(self, file_path: str, guess: bool = False, silent: bool = False) -> str:
        """
        Formats the name of a movie file.

        :param file_path: The path of the movie file.
        :param guess: Whether to try to guess the movie title based on the file name, if the title is not found in the file
                      name.
        :param silent: Whether to ask the user for confirmation before using the guessed movie title.
        :return: The formatted name of the movie file, or None if the file extension is not supported.
        """
        file_extension = os.path.splitext(filename)[1]

        # Remove file extension
        filename_without_ext = os.path.splitext(filename)[0]

        # Split filename into parts
        parts = filename_without_ext.split('.')

        # Remove any non-alphanumeric characters from each part
        for i in range(len(parts)):
            parts[i] = re.sub('[^0-9a-zA-Z]+', '', parts[i])

        # If the last part is a four digit number, assume it's the year and remove it
        if parts[-1].isdigit() and len(parts[-1]) == 4:
            parts.pop()

        # Join the parts with spaces and capitalize each word
        title = ' '.join(parts).title()

        # Fetch data for the movie from OMDb API
        data = fetch_movie_data(title)

        # Construct the new filename according to the Plex naming convention
        if data is not None:
            new_filename = f'{data["Title"]} ({data["Year"]})'
            if 'imdbID' in data:
                new_filename += f' ({data["imdbID"]})'
            new_filename += file_extension
        
            return new_filename
        return None

    def guess_movie_title(self, filename: str) -> str:
        """
        Attempts to guess the title of a movie from its file name.

        :param filename: The name of the movie file.
        :return: The guessed title of the movie, or None if the title could not be guessed.
        """
        # Remove any known file extensions
        file_title = re.sub(r'\.(avi|mp4|mkv|mov)$', '', file_title, flags=re.IGNORECASE)

        # Remove common strings
        file_title = self.remove_common_strings(file_title)

        # Split the remaining string by common delimiters
        delimiters = ['.', '-', '_', ' ']
        for delimiter in delimiters:
            words = file_title.split(delimiter)
            # If we have more than two words, assume the last two words are the movie title
            if len(words) > 2:
                return delimiter.join(words[-2:]).title()

        # If we couldn't guess a movie title, return the original file title
        return file_title.title()
        
    def request_movie_data(self, title: str, year: Optional[str] = None, guess: bool, silent: bool) -> dict:
        """
        Function to fetch movie data from OMDb API.

        Args:
            movie_title (str): The title of the movie to search for.
            api_key (str): The OMDb API key to use for the request.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the movie data if the API request was successful,
            otherwise None.

        Raises:
            requests.exceptions.HTTPError: If the API request returns an error.

        """

        url = f'http://www.omdbapi.com?apikey={api_key}&t={title}'

        # Make a request to the OMDb API
        response = requests.get(url)
        data = json.loads(response.text)
        
        params = {"apikey": api_key, "t": title}
        if year:
            params["y"] = year
        response = requests.get("http://www.omdbapi.com/", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def fetch_movie_data(self, title: str, year: Optional[str] = None, guess: bool = False, silent: bool = False) -> dict:
        """
        Fetches movie data from the OMDB API.

        Args:
            title (str): The title of the movie.
            year (str, optional): The year the movie was released. Defaults to None.
            guess (bool): If true, the program will try to guess the movie title if not found on OMDB. Defaults to False.
            silent (bool): If true, the program will not ask for user input. Defaults to False.

        Returns:
            dict: A dictionary containing movie data, or an empty dictionary if no data was found.
        """

        # Try to get data from OMDB API
        movie_data = self.request_movie_data(title, year)

        # If movie data is empty and guess is enabled, try to guess the movie title
        if not movie_data and guess:
            guess_title = self.guess_movie_title(title)
            if guess_title != title:
                if not silent:
                    response = input(f"Do you want to search for '{guess_title}' instead? (Y/n)")
                    if response.lower() == 'n':
                        return {}
                movie_data = self.get_movie_data(guess_title, year)

        # Return the movie data
        return movie_data


    def rename_and_move_movie(self, pathname: str, silent: bool = False, guess: bool = False) -> None:
        """
        Renames and moves a movie file to a new directory based on the movie title.
        
        Args:
            pathname (str): The path to the movie file.
            silent (bool): If true, the program will not ask for user input. Defaults to False.
            guess (bool): If true, the program will try to guess the movie title if not found on OMDB. Defaults to False.
        """
        file_ext = os.path.splitext(filename)[1];
        if file_ext not in ["avi","mp4","mkv","mov"] :
            return

        # Extract the filename from the pathname
        filename = os.path.basename(pathname)

        # Fetch movie data
        movie_data = self.fetch_movie_data(filename, guess=guess, silent=silent)

        # Format movie title
        movie_title = self.format_movie_name(movie_data)

        # Rename movie file 
        new_filename = movie_title + file_ext 
        if new_filename != filename:
            new_pathname = os.path.join(os.path.dirname(pathname), new_filename)
            if not os.path.exists(new_pathname):
                try:
                    os.rename(pathname, os.path.join(os.path.dirname(pathname), new_filename))
                except OSError as e:
                    print(f"Error renaming file {filename}: {e}")
            else: 
                print("Warning! File name already exists. Skipping")

        # Rename directory
        directory = os.path.dirname(pathname)
        new_directory = os.path.join(directory, movie_title)
        if new_directory != directory:
            try:
                os.rename(directory, new_directory)
            except OSError as e:
                print(f"Error renaming directory {directory}: {e}")


    def remove_common_strings(filename): 
        """
        Removes common strings from a given filename.

        Args:
            filename (str): The filename to remove common strings from.

        Returns:
            str: The updated filename with common strings removed.
        """
        if os.path.exists(COMMON_STRINGS_FILE):
            with open(COMMON_STRINGS_FILE, "r") as f:
                common_strings = f.readlines()
                # Remove newline characters from each line
                common_strings = [s.strip() for s in common_strings]
        else:
            # If the common strings file doesn't exist, create an empty list
            common_strings = []

        # Remove common strings from filename
        for s in common_strings:
            filename = filename.replace(s, "")

        return filename

    def save_common_strings(common_strings):
        """
        Saves the list of common strings to a persistent file.

        Args:
            common_strings: A list of strings to be saved to the persistent file.

        Returns:
            None
        """
        with open(COMMON_STRINGS_FILE, "w") as f:
            for s in common_strings:
                f.write(s + "\n")
