import argparse
import os
import sys
sys.path.append('.')
from pathlib import Path

from keys import OMDB_API_KEY
from plex_media_organizer import PlexMediaOrganizer

sys.path.append('src/')

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Organize media files in a directory')
    parser.add_argument('path', type=Path, help='path to the directory containing the media files')
    parser.add_argument('--guess', action='store_true', help='guess movie titles if not found on OMDB')
    parser.add_argument('--silent', action='store_true', help='run without user input')
    parser.add_argument('--recursive', action='store_true', help='recurse into subdirectories')
    args = parser.parse_args()

    # Initialize PlexMediaOrganizer object
    organizer = PlexMediaOrganizer(api_key=os.environ.get('OMDB_API_KEY') or OMDB_API_KEY)

    if not os.path.exists(args.path):
        print(f"Error: Path {args.path} does not exist")
        return

    if os.path.isfile(args.path):
        organizer.rename_and_move_movies(args.path, guess=args.guess, silent=args.silent)
    else:
        files = []
        if args.recurse:
            for (dirpath, _, filenames) in os.walk(args.path):
                for filename in filenames:
                    files.append(os.path.join(dirpath, filename))
        else:
            files = [os.path.join(args.path, f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(directory, f))]

            for f in files:
                organizer.rename_and_move_movies(f, guess=args.guess, silent=args.silent)

if __name__ == '__main__':
    main()
