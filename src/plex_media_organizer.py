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

    def guess_title(self, file_path: str) -> str:
        """
        Attempts to guess the title of a movie from its file name.

        :param file_name: The name of the movie file.
        :return: The guessed title of the movie, or None if the title could not be guessed.
        """
        # Remove any known file extensions
        file_title = re.sub(r'\.(avi|mp4|mkv|mov)$', '', file_title, flags=re.IGNORECASE)

        # Split the remaining string by common delimiters
        delimiters = ['.', '-', '_', ' ']
        for delimiter in delimiters:
            words = file_title.split(delimiter)
            # If we have more than two words, assume the last two words are the movie title
            if len(words) > 2:
                return delimiter.join(words[-2:]).title()

        # If we couldn't guess a movie title, return the original file title
        return file_title.title()
        
    def fetch_movie_data(self, title: str, year: Optional[str] = None) -> dict:
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

    def rename_move_files(self, dir_path: str, silent: bool = False) -> None:
        """
        Renames and moves movie files from a source directory to a destination directory.

        :param source_dir: The source directory containing the movie files.
        :param destination_dir: The destination directory where the movie files will be moved to.
        :param delete_source: Whether to delete the original movie files from the source directory after moving them.
        :param skip_existing: Whether to skip files that already exist in the destination directory.
        :param ignore_extensions: A list of file extensions to ignore when processing movie files.
        :param ignore_regex: A regular expression pattern to match filenames to ignore when processing movie files.
        """

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

    def organize_directory(self, directory: str, silent: bool = False) -> None:
        """
        Organizes a directory by renaming all movie files in the directory and its subdirectories.
        Args:
            directory: The path to the directory to be organized.
            silent: A flag to run the function silently without prompting for user input.
        """
        # Get list of all movie files in directory and subdirectories
        movie_files = get_movie_files(directory)

        # Iterate through each movie file and rename it
        for file_path in movie_files:
            new_file_path = format_movie_name(file_path)
            os.rename(file_path, new_file_path)
            print(f"Renamed file: {file_path} -> {new_file_path}")
        
        # Remove common strings from movie file names
        remove_common_strings(directory)

        # Print completion message
        print("Directory organization complete!")


    def rename_movie_files(directory, extension):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(extension):
                    old_path = os.path.join(root, filename)
                    new_filename = format_movie_name(filename)
                    new_path = os.path.join(root, new_filename)
                    os.rename(old_path, new_path)
                    print(f'Renamed {filename} to {new_filename}')

