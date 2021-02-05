import secrets
from plexapi.server import PlexServer
import os.path, time
from datetime import datetime, timedelta

baseurl = 'http://%s:32400' % secrets.plex_ip
plex = PlexServer(baseurl, secrets.plex_token)
tv_shows = plex.library.section("TV Shows")
optimizations = next((x for x in tv_shows.folders() if x.title == 'Plex Versions'), None)

# horrible implementation - rewrite later if i feel like it
for folder1 in optimizations.subfolders():
    for folder2 in folder1.subfolders():
        for folder3 in folder2.subfolders():
            for folder4 in folder3.subfolders():
                optimized_versions = [version for version in folder4.media if version.title != 'Original']
                for optimized_version in optimized_versions:
                    file = optimized_version.parts[0].file
                    file_age = difference = datetime.now() - datetime.fromtimestamp(os.path.getctime(file))
                    if file_age > timedelta(days = 30, hours = 0, minutes = 0):
                        print("Deleting: %s" % file)
                        optimized_version.delete()
