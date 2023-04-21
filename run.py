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
    parser.add_argument('--silent', action='store_true', help='run without user input')
    parser.add_argument('--recursive', action='store_true', help='recurse into subdirectories')
    args = parser.parse_args()

    # Initialize PlexMediaOrganizer object
    organizer = PlexMediaOrganizer(api_key=os.environ.get('OMDB_API_KEY') or OMDB_API_KEY)

    if not os.path.exists(args.path):
        print(f"Error: Path {args.path} does not exist")
        return

    if os.path.isfile(args.path):
        changes = organizer.plan_filepath_changes(args.path, silent=args.silent, recurslive=args.recursive)
        organizer.execute_filepath_changes(changes)

if __name__ == '__main__':
    main()
