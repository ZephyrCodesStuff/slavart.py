#!/usr/bin/env python3

import argparse
import logging
import coloredlogs
import json
import pathvalidate

from httpx import Client
from structs import *
from typing import List
from pathlib import Path

log = logging.getLogger(__name__)
coloredlogs.install(level='INFO', fmt='%(asctime)s %(levelname)s %(message)s', logger=log)

parser = argparse.ArgumentParser(description='Quick script to download music from https://slavart.gamesdrive.com.')
parser.add_argument('-q', '--query', metavar='query', type=str, help='Query to search for')
parser.add_argument('-i', '--id', metavar='id', type=int, nargs="+", help='ID of the song')
parser.add_argument('-o', '--output', metavar='output', type=str, default='', help='Output folder')
parser.add_argument('-t', '--timeout', metavar='timeout', type=float, default='90.0', help='API response timeout')
args = parser.parse_args()

ENDPOINT = "https://slavart.gamesdrive.net/api"
ENDPOINT_API = "https://slavart-api.gamesdrive.net/api"

def search(client: Client, query: str) -> Results:
    response = client.get(f"{ENDPOINT}/search?q={query}")
    if response.status_code == 200:
        return Results.from_dict(response.json())

def download(client: Client, id: int, path: Path) -> str:
    response = client.get(f"{ENDPOINT_API}/download/track?id={id}")
    if response.status_code == 200:
        track: Optional[None]
        file_name = f"{id}.flac"

        try:
            with open("tracks.json", "r") as f:
                tracks = json.loads(f.read()) if f.read() != "" else []
                tracks = list(filter(lambda track: track['id'] == id, tracks))

                if len(tracks) > 0:
                    track = tracks[0]
        except OSError:
            pass

        if track is not None:
            path = path.joinpath(track['artist']).joinpath(track['album'])
            file_name = f"{track['track_number']} - {track['title']}.flac"
        else:
            path = path.joinpath("Uncategorized")

        path = pathvalidate.sanitize_filepath(path)
        file_name = pathvalidate.sanitize_filename(file_name)

        if not path.exists():
            path.mkdir(parents=True)
        
        path = path.joinpath(file_name)

        log.info(f"Downloading '{file_name}'...")
        with open(path, "wb") as f:
            f.write(response.content)
        
        return file_name


def main():
    client = Client(timeout=args.timeout)

    if args.id is not None:
        path = Path(args.output)

        for id in args.id:
            log.info(f"Fetching track with ID '{id}'...")
            file_name = download(client, id, path=path) 
            log.info(f"Successfully downloaded '{file_name}'.")
    else:
        if args.query is None:
            log.error("You must specify a query or an ID")
            exit(1)

        results = search(client, args.query)

        log.info(f"Found {results.tracks.total} tracks for query '{args.query}'")
        for track in results.tracks.items:
            log.info(track.to_string())

        if len(results.tracks.items) > 0:
            with open("tracks.json", "w+") as f:
                tracks: List[dict] = json.loads(f.read()) if f.read() != "" else []
                tracks.append([track.to_dict() for track in results.tracks.items if track.id not in [track['id'] for track in tracks]])
                f.write(json.dumps(tracks, indent=4, sort_keys=True, separators=(', ', ': ')))

if __name__ == "__main__":
    main()