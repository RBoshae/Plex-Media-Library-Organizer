import argparse
import os
from pathlib import Path

from plex_media_organizer import PlexMediaOrganizer
import omdb_api_key

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Organize media files in a directory')
    parser.add_argument('path', type=Path, help='path to the directory containing the media files')
    parser.add_argument('--guess', action='store_true', help='guess movie titles if not found on OMDB')
    parser.add_argument('--silent', action='store_true', help='run without user input')
    args = parser.parse_args()

    # Initialize PlexMediaOrganizer object
    organizer = PlexMediaOrganizer(api_key=os.environ.get('OMDB_API_KEY') or omdb_api_key.OMDB_API_KEY)

    # Organize media files in the given directory
    organizer.organize_directory(args.path, guess=args.guess, silent=args.silent)


if __name__ == '__main__':
    main()
