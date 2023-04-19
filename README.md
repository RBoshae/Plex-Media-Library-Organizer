# Plex Movie Organizer

**Note**: This project is still a work in progress and may not be fully
functional yet. Contributions and feedback are welcome!

Plex Movie Organizer is a Python tool that helps you organize your movie files
in a Plex-friendly format by fetching movie information from the OMDb API and
renaming the movie files and directories accordingly.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-repo/plex-movie-organizer.git
```

2. Change the working directory to `plex-movie-organizer`:

```bash
cd plex-movie-organizer
```

3. Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## OMDb API Setup

To use Plex Movie Organizer, you need an API key from OMDb.

1. Sign up for an API key at [OMDb API](https://www.omdbapi.com/apikey.aspx).

2. Create a `keys.py` file in the root of the `plex-movie-organizer` directory
   with the following content:

```python
OMDB_API_KEY = 'your_api_key_here'
```

Replace your_api_key_here with the API key you received from OMDb.

## User Specified Strings

To remove specific strings from movie titles, create a
user_specified_strings.txt file in the root of the plex-movie-organizer
directory. Each line of the file should contain a string you want to remove
from the movie titles. For example:

```
example.string.1
example.string.2
```

The program will automatically remove these strings from the movie titles when
renaming them.

## Usage

Once you have set up the OMDb API key and created the keys.py and
user_specified_strings.txt files, you can use the Plex Movie Organizer to rename
and organize your movie files.

### Using the run.py script

You can use the included run.py script to quickly rename movies by providing the
path to your movie folder as an argument. You can also use the --recursive flag
to process movies in subdirectories.

```bash
python run.py --path "/path/to/your/movie/folder" --recursive
```

This command will process all movie files in the specified folder and its
subdirectories, fetch movie information from the OMDb API, and rename the files
and directories accordingly.

### Using the Plex Movie Organizer in your own script

Here's a basic example of how to use the Plex Movie Organizer in your own Python
script:

```python
from plex_movie_organizer import PlexMovieOrganizer

# Initialize the Plex Movie Organizer
organizer = PlexMovieOrganizer()

# Plan the filepath changes
pathname = "/path/to/your/movie/folder"
planned_changes = organizer.plan_filepath_changes(pathname, recursive=True)

# Execute the planned changes
organizer.execute_filepath_changes(planned_changes)
```

This example will process all movie files in the specified folder and its
subdirectories, fetch movie information from the OMDb API, and rename the files
and directories accordingly.

## Contributing

If you'd like to contribute to Plex Media Organizer, please submit a pull
request or open an issue on this repository. We welcome contributions of all
kinds, including bug fixes, feature requests, and documentation improvements.
