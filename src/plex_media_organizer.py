import json
import os
import requests
import re
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_dir)

from typing import Optional

from config import USER_SPECIFIED_STRINGS_FILE
from keys import OMDB_API_KEY


class PlexMediaOrganizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Creates an instance of the PlexMediaOrganizer class.

        :param api_key: (Optional) The API key to use for requests to the OMDb API. If not provided, it will look for the
                        key in the environment variable "OMDB_API_KEY". If not found there, it will try to import the key
                        from a module named "keys" in the current working directory.
        """

        if api_key is None:
            api_key = os.environ.get('OMDB_API_KEY') or OMDB_API_KEY
        self.api_key = api_key

    def remove_user_specified_strings(self, name: str): 
        """
        Removes user spefied strings listed in  from a given filename.

        Args:
            filename (str): The filename to remove common strings from.

        Returns:
            str: The updated filename with common strings removed.
        """
        if os.path.exists(USER_SPECIFIED_STRINGS_FILE):
            with open(USER_SPECIFIED_STRINGS_FILE, "r") as f:
                user_specified_strings = f.readlines()
                # Remove newline characters from each line
                user_specified_strings = [s.strip() for s in user_specified_strings]
        else:
            # If the common strings file doesn't exist, create an empty list
            user_specified_strings = []

        # Remove common strings from filename
        for s in user_specified_strings:
            name = name.replace(s, "")

        return name

    def save_common_strings(common_strings):
        """
        Saves the list of common strings to a persistent file.

        Args:
            common_strings: A list of strings to be saved to the persistent file.

        Returns:
            None
        """
        with open(USER_SPECIFIED_STRINGS_FILE, "w") as f:
            for s in common_strings:
                f.write(s + "\n")
    def fetch_movie_data(self, title: str, year: Optional[str] = None, silent: bool = False) -> dict:
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
        if not movie_data:
            if not silent:
                response = input(f"Unable to fetch movie data for {title}. To try again, please specify a movie title to search for? (Press Enter to skip)")
                if response != '':
                   # TODO Implement
                   # self.format_movie_name(response) 
                   print ("Not yet implemented, skipping for now")

        # Return the movie data
        return movie_data

    def format_movie_name(self, filename: str, guess: bool = False, silent: bool = False) -> str:
        """
        Formats the name of a movie file.

        :param filename: The name of the file.
        :param guess: Whether to try to guess the movie title based on the file name, if the title is not found in the file
                      name.
        :param silent: Whether to ask the user for confirmation before using the guessed movie title.
        :return: The formatted name of the movie file, or None if the file extension is not supported.
        """
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

        # Remove User Specified Strings
        title = self.remove_user_specified_strings(name=title)

        # Fetch data for the movie from OMDb API
        data = self.fetch_movie_data(title=title)

        # Construct the new filename according to the Plex naming convention
        if data is not None:
            new_filename = f'{data["Title"]} ({data["Year"]})'
            if 'imdbID' in data:
                new_filename += f' ({data["imdbID"]})'
        
            return new_filename
        return None

        # If we couldn't guess a movie title, return the original file title
        return filename.title()
        
    def request_movie_data(self, title: str, year: Optional[str] = None) -> dict:
        """
        Function to fetch movie data from OMDb API.

        Args:
            title (str): The title of the movie to search for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the movie data if the API request was successful,
            otherwise None.

        Raises:
            requests.exceptions.HTTPError: If the API request returns an error.

        """

        # Create a dictionary to store the API parameters
        params = {"apikey": self.api_key, "t": title}

        # Add the year parameter if it is provided
        if year:
            params["y"] = year

        # Make a request to the OMDb API
        response = requests.get("http://www.omdbapi.com/", params=params)

        # Check if the request was successful and return the JSON data if it was
        if response.status_code == 200:
            return response.json()
        else:
            return None

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

