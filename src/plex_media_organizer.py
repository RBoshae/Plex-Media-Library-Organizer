import json
import os
import requests
import re
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_dir)

from typing import Dict, List, Optional, Tuple

from config import USER_SPECIFIED_STRINGS_FILE
from keys import OMDB_API_KEY


class PlexMovieOrganizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Creates an instance of the PlexMediaOrganizer class.

        :param api_key: (Optional) The API key to use for requests to the OMDb
                        API. If not provided, it will look for the key in the
                        environment variable "OMDB_API_KEY". If not found there, 
                        it will try to import the key from a module named "keys"
                        in the current working directory.
        """

        if api_key is None:
            api_key = os.environ.get('OMDB_API_KEY') or OMDB_API_KEY
        self.api_key = api_key

    def execute_filepath_changes(self, changes: Dict[str, str]) -> None:
        """
        Executes the planned filepath change to rename and move movie files.

        Args:
            changes (Dict[str, str]): A dictionary containing the original
            filepaths as keys and the filepaths to change to as values.

        Returns:
            None
        """
        for old_path, new_path in changes.items():
            # Create directories in the new file path if they don't exist
            new_dir = os.path.dirname(new_path)
            if not os.path.exists(new_dir):
                try:
                    os.makedirs(new_dir)
                except OSError as e:
                    print(f"Error creating directory {new_dir}: {e}")
                    continue

            # Rename the file
            if not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                except OSError as e:
                    print(f"Error renaming file {old_path}: {e}")
            else:
                print(f"Warning! File {new_path} already exists. Skipping")

    def fetch_movie_data(self, title: str, year: Optional[str] = None, silent: bool = False) -> dict:
        """
        Fetches movie data from the OMDB API.

        Args:
            title (str): The title of the movie.
            year (str, optional): The year the movie was released. Defaults to None.
            silent (bool): If true, the program will not ask for user input.
                           Defaults to False.

        Returns:
            dict: A dictionary containing movie data, or an empty dictionary if
            no data was found.
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

    def get_movie_title_from_pathname(pathname: str) -> str:
        """
        Extracts the movie title from a file path.

        Args:
            pathname (str): The path to the movie file.

        Returns:
            str: The extracted movie title.
        """
        # Extract the filename from the pathname
        filename = os.path.basename(pathname)

        # Remove the file extension from the filename
        movie_title, _ = os.path.splitext(filename)

        return movie_title

    def clean_movie_title(self, title:str) -> str:

        # Split filename into parts
        parts = title.split('.')

        # Remove any non-alphanumeric characters from each part
        for i in range(len(parts)):
            parts[i] = re.sub('[^0-9a-zA-Z]+', '', parts[i])
        
        # If the last part is a four digit number, assume it's the year and remove it
        if parts[-1].isdigit() and len(parts[-1]) == 4:
            parts.pop()

        # Join the parts with spaces and capitalize each word
        partially_clean_filename = ' '.join(parts).title()

        # Remove User Specified Strings
        clean_filename = self.remove_user_specified_strings(name=partially_clean_filename)

        return clean_filename
        

    def format_movie_name(self, movie_data) -> str:
        """
        Formats the name of a movie file.

        :param filename: The name of the file.
        :param silent: Whether to ask the user for confirmation before using
                       the guessed movie title.
        :return: The formatted name of the movie file, or None if the file
                 extension is not supported.
        """

        # Construct the new filename according to the Plex naming convention
        if movie_data is not None:
            new_filename = f'{movie_data["Title"]} ({movie_data["Year"]})'
            if 'imdbID' in movie_data:
                new_filename += f' ({movie_data["imdbID"]})'
        
            return new_filename
        return None

    def plan_filepath_changes(self, pathname: str, recursive: bool = False) -> Dict[str, str]:
        """
        Plans the renaming and moving of a movie file.

        Args:
            pathname (str): The path to the movie file.
            recursive (bool, optional): If True, the function will recurse into
                                        subdirectories

        Returns:
            Dict[str, str]]: A dictionary containing the original filepaths and
                             the filepaths to change to, or None if no changes 
                             are needed.
        """
        planned_changes = {}
        
        def process_path(pathname: str) -> Optional[Tuple[str, str]]:
            file_ext = os.path.splitext(pathname)[1]
            if file_ext not in [".avi", ".mp4", ".mkv", ".mov"]:
                return None

            # Extract the filename from the pathname
            filename = os.path.basename(pathname)

            raw_title = get_movie_title_from_pathname(pathname)
            
            title = clean_movie_title(raw_title)

            # Fetch movie data
            movie_data = self.fetch_movie_data(title) 

            # Format movie title
            movie_title = self.format_movie_name(movie_data)

            # Construct new file path
            new_filename = movie_title + file_ext
            new_pathname = os.path.join(os.path.dirname(pathname), new_filename)

            if new_pathname != pathname:
                return pathname, new_pathname
            else:
                return None

        if recursive:
            for dirpath, _, filenames in os.walk(pathname):
                for filename in filenames:
                    old_path = os.path.join(dirpath, filename)
                    change = process_path(old_path)
                    if change:
                        planned_changes[change[0]] = change[1]

                # Plan directory name change
                if planned_changes:
                    old_dir = os.path.basename(dirpath)
                    first_new_path = next(iter(planned_changes.values()))
                    movie_title = os.path.splitext(os.path.basename(first_new_path))[0]
                    parent_dir = os.path.dirname(dirpath)
                    new_dirpath = os.path.join(parent_dir, movie_title)
                    if new_dirpath != dirpath:
                        planned_changes[dirpath] = new_dirpath
        else:
            change = process_path(pathname)
            if change:
                planned_changes[change[0]] = change[1]
                
        return planned_changes

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

        
    def request_movie_data(self, title: str, year: Optional[str] = None) -> dict:
        """
        Function to fetch movie data from OMDb API.

        Args:
            title (str): The title of the movie to search for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the movie data if
                                      the API request was successful,
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
