# Media Library Organizer

Media Library Organizer is a Python program that renames movie files in a digital library according to the Plex naming convention.

## Installation

To use Media Library Organizer, you'll need to have Python 3 installed on your system. You can download Python from the official website: https://www.python.org/downloads/

You'll also need to install the `requests` module, which can be installed using pip:

Once you have Python and `requests` installed, download the `media_library_organizer.py` file from this repository and save it to your computer.

## Usage

To use Media Library Organizer, you'll need to have a digital library of movies in a folder on your computer. The movies should be in MP4 format and named in a way that includes the movie title and year, separated by spaces or dots. For example: `The Shawshank Redemption (1994).mp4`.

To run Media Library Organizer, open a terminal window and navigate to the folder where you saved the `media_library_organizer.py` file. Then, run the following command:

Replace `/path/to/your/digital/library/` with the path to the folder containing your movie files, and `mp4` with the file extension of your movie files if it's different from `.mp4`.

Media Library Organizer will iterate over all movie files in the specified folder, fetch data for each movie from the OMDb API, and rename the files according to the Plex naming convention. The new file names will include the movie title, year, and optional IMDb ID, separated by dashes.

## Contributing

If you'd like to contribute to Media Library Organizer, please submit a pull request or open an issue on this repository. We welcome contributions of all kinds, including bug fixes, feature requests, and documentation improvements.
