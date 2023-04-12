import json
import os
import requests
import re

# Function to fetch movie data from OMDb API
def fetch_movie_data(title, year=None):
    api_key = 'YOUR_OMDB_API_KEY'
    url = f'http://www.omdbapi.com?apikey={api_key&t={title}'

    # Make a request to the OMDb API
    response = requests.get(url)
    data = json.loads(response.text)
    
    params = {"apikey": OMDB_API_KEY, "t": title}
    if year:
        params["y"] = year
    response = requests.get("http://www.omdbapi.com/", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to format movie name
def format_movie_name(filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[1]

    # Remove file extension
    filename_witout_ext = os.path.splitext(filename)[0]

    # Split filename into parts
    parts = file_name_without_ext.split('.')

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
    new_filename = f'{data["Title"]} ({data["Year"]})'
    if 'imdbID' in data:
        new_filename += f' ({data["imdbID"})'
    new_filename += file_extension
    
    return new_filename



# Function to rename movie files using Plex naming convention
def rename_movie_files(directory, extension):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                old_path = os.path.join(root, filename)
                new_filename = format_movie_name(filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f'Renamed {filename} to {new_filename}')

# Example usage
directory = "/path/to/your/digital/library/"
extension = "mp4"
rename_movie_files(path, extension)

