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
                return None # TODO Remove return None and implement lines below
                if response != '':
                   # TODO Implement
                   # self.format_movie_name(response) 
                   print ("Not yet implemented, skipping for now")

        # Return the movie data
        return movie_data

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
        

    def format_movie_filename(self, movie_data: dict) -> str:
        """
        Formats the name of a movie file.

        Args:
            movie_data (dict): The collection containing movie information.

        Returns:
            str: The formatted name of the movie file
        """

        # Construct the new filename according to the Plex naming convention
        if movie_data is not None:
            new_filename = f'{movie_data["Title"]} ({movie_data["Year"]})'
            if 'imdbID' in movie_data:
                new_filename += f' ({movie_data["imdbID"]})'
        
            return self.remove_invalid_chars(new_filename)
        return None


    def format_movie_dirname(self, movie_data:dict) -> str:
        """
        Formats the name of the movie directory

        Args:
            movie_data (dict): The collection containing movie information.

        Returns:
            str: The formatted name of the movie directory
        """
        if movie_data is not None:
            new_dirname = f'{movie_data["Title"]} ({movie_data["Year"]})'
            return self.remove_invalid_chars(new_dirname)
        return None

    def remove_invalid_chars(self, input_str: str, os_type: str = 'windows') -> str:
        """
        Removes all invalid characters from a string, making it suitable for use as a movie name or directory name.

        Args:
            input_str (str): The input string to process.
            os_type (str, optional): The target operating system. Either 'windows', 'macos', or 'linux'. Defaults to 'windows'.

        Returns:
            str: The processed string with invalid characters removed.
        """

        # Define the invalid characters based on the target operating system
        if os_type == 'windows':
            invalid_chars = r'[<>:"/\\|?*]'
        elif os_type in ['macos', 'linux']:
            invalid_chars = r'[/\0]'
        else:
            raise ValueError(f"Unsupported os_type: {os_type}. Use 'windows', 'macos', or 'linux'.")

        # Remove invalid characters using a regular expression
        cleaned_str = re.sub(invalid_chars, '', input_str)

        return cleaned_str

    def plan_changes(self, dir_path: str, recursive: bool = False) -> Dict[str, str]:
        """
        Plans the renaming and moving of a movie file.

        Args:
            dir_path (str): The directory path to the movie file(s).
            recursive (bool, optional): If True, the function will recurse into
                                        subdirectories

        Returns:
            Dict[str, str]]: A dictionary containing the original filepaths and
                             the filepaths to change to, or None if no changes 
                             are needed.
        """
        changes = {}
        
        def plan_change(file_path: str) -> Optional[Tuple[str, str]]:
            file_ext = os.path.splitext(file_path)[1]
            if file_ext not in [".avi", ".mp4", ".mkv", ".mov"]:
                return None

            # Extract the filename from the pathname
            filename = os.path.basename(file_path)

            filename_without_ext, _ = os.path.splitext(filename)
            
            clean_title = self.clean_movie_title(filename_without_ext)

            # Fetch movie data
            movie_data = self.fetch_movie_data(clean_title) 

            if movie_data is None:
                print(f"Unable to query filename: {filename}")
                return

            # Format movie title
            formatted_movie_filename = self.format_movie_filename(movie_data)

            # Format directory name
            formatted_movie_dirname = self.format_movie_dirname(movie_data)

            parent_dir = os.path.dirname(os.path.dirname(file_path))

            # Construct new file path
            new_filename = formatted_movie_filename + file_ext
            new_parent_dir = os.path.join(parent_dir, formatted_movie_dirname)
            new_pathname = os.path.join(new_parent_dir, new_filename)

            if new_pathname != file_path:
                return file_path, new_pathname
            else:
                return None

        if recursive:
            for dirpath, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    change = plan_change(file_path)
                    if change:
                        changes[change[0]] = change[1]
        else:
            for filename in os.listdir(dir_path):
                full_path = os.path.join(dir_path, filename)
                if os.path.isfile(full_path):
                    change = plan_change(full_path)
                    if change:
                        changes[change[0]] = change[1]
                
        return changes

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

    def print_planned_changes(self, changes: Dict[str, str]) -> None:
        print("Ppreview_changeslanned changes:")
        for old_path, new_path in changes.items():
            print(f"{old_path} -> {new_path}")

