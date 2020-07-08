#!/usr/bin/env python

import musicbrainzngs as mb
import dateutil.parser
import glob
import os
import json
import shutil

def do_copy(opt):
    files = sorted(glob.glob(opt.mp3_pattern),
                   key=lambda a: int(os.path.splitext(os.path.basename(a))[0]))
    tracks = json.load(open(opt.track_list))
    for i,f in enumerate(files):
        filename = tracks[i]["FILE"]
        #print(f"mv -i {f} {filename}")
        shutil.copy2(f, filename)

def show_track_list(opt):
    if opt.genre is None:
        raise ValueError("ERROR: a genre must be specified.")
    db = json.load(open(opt.release_file))
    db = db["disc"]
    if db["release-count"] != 1:
        raise ValueError("ERROR: release-count is not 1")
    #
    release = db["release-list"][0]
    #
    release_year = dateutil.parser.parse(release["date"]).year
    album_title = release["title"]
    if len(release["artist-credit"]) == 0:
        raise ValueError("ERROR: artist-credit is not there.")
    artist_name = release["artist-credit"][0]["artist"]["name"]
    #
    if release["medium-count"] != 1:
        raise ValueError("ERROR: medium-count is not 1")
    #
    media = release["medium-list"][0]
    track_count = media["track-count"]
    if track_count != len(media["track-list"]):
        raise ValueError("ERROR: the length of track-list is not matched.")
    toc = []
    for track in media["track-list"]:
        track_nb = track["number"]
        track_title = track["recording"]["title"]
        toc.append({
            "FILE": f"""[{artist_name}][{album_title}][{track_nb}][{track_title}].mp3""",
            "TPE1": artist_name,
            "TALB": album_title,
            "TYER": f"""{release_year}""",
            "TCON": f"""{opt.genre}""",
            "TRCK": f"""{track_nb}/{track_count}""",
            "APIC": f"""[{artist_name}][{album_title}].jpg""",
            "TIT2": f"""{track_title}""",
            })
    #
    print(json.dumps(toc, indent=opt.indent))

def search_artist(opt):
    print(json.dumps(mb.search_artists(opt.artist), indent=opt.indent))

def get_artist_by_id(opt):
    #inc = [ "artists", "recordings" ]
    print(json.dumps(mb.get_artist_by_id(opt.artist_id),
                     indent=opt.indent))

def get_releases_by_id(opt):
    inc = [ "artists", "recordings" ]
    print(json.dumps(mb.get_releases_by_discid(opt.disc_id, includes=inc),
                     indent=opt.indent))

def get_releases_by_discid(opt):
    inc = [ "artists", "recordings" ]
    print(json.dumps(mb.get_releases_by_discid(opt.disc_id, includes=inc),
                     indent=opt.indent))

def get_recording_by_id(opt):
    inc = [ "artists" ]
    print(json.dumps(mb.get_recording_by_id(opt.recording_id, includes=inc),
                     indent=opt.indent))

valid_genre_map = {
        "metal": "heavy metal",
        "rock": "hard rock",
        "pop": "pop",
        "jpop": "jpop",
        }
valid_genre_alias = list(valid_genre_map.keys())

def main():
    from argparse import ArgumentParser
    from argparse import ArgumentDefaultsHelpFormatter
    ap = ArgumentParser(
            description="utility to access Music Brainz.",
            formatter_class=ArgumentDefaultsHelpFormatter)
    #ap.add_argument("arg1", metavar="ARG1", help="1st item.")
    #ap.add_argument("arg2", metavar="ARG2", help="2nd item.")
    ap.add_argument("-a", action="store", dest="artist",
                    help="specify a part of or the name of artist.")
    ap.add_argument("-f", "--release-file", action="store", dest="release_file",
                    help="specify a JSON file containing the release.")
    ap.add_argument("-g", action="store", dest="genre_alias",
                    choices=valid_genre_alias,
                    help=f"specify a genre in either {valid_genre_alias}")
    ap.add_argument("--artist-id", action="store", dest="artist_id",
                    help="specify a Music Brainz id of the artist.")
    ap.add_argument("--release-id", action="store", dest="release_id",
                    help="specify a release Id of the release.")
    ap.add_argument("--disc-id", action="store", dest="disc_id",
                    help="specify a Disc Id of the release.")
    ap.add_argument("--recording-id", action="store", dest="recording_id",
                    help="specify a recording Id of the track.")
    ap.add_argument("-i", "--indent", action="store", dest="indent",
                    type=int, default=4,
                    help="specify the number of indent.")
    ap.add_argument("--no-indent", action="store_false", dest="enable_indent",
                    help="disable to indent the output.")
    ap.add_argument("-r", action="store", dest="track_list",
                    help="copy mp3 files to new mp3 files with the track list.")
    ap.add_argument("--mp3-files", action="store", dest="mp3_pattern",
                    default="*.mp3",
                    help="specify a glob to be copied.")
    ap.add_argument("-v", action="store_true", dest="verbose",
                    help="enable verbose mode.")
    opt = ap.parse_args()
    opt.genre = None
    if opt.genre_alias:
        opt.genre = valid_genre_map[opt.genre_alias]
    if opt.enable_indent == False:
        opt.indent = None
    #
    mb.set_useragent("application", "0.01", "http://example.com")
    if opt.artist:
        search_artist(opt)
    elif opt.artist_id:
        get_artist_by_id(opt)
    elif opt.disc_id:
        get_releases_by_discid(opt)
    elif opt.recording_id:
        get_recording_by_id(opt)
    elif opt.release_file:
        show_track_list(opt)
    elif opt.track_list:
        do_copy(opt)
    else:
        ap.print_help()

if __name__ == "__main__" :
    main()
