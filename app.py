import pandas as pd
import requests
import io
import json
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import secrets
from plexapi.server import PlexServer
import os.path, time
from datetime import datetime, timedelta

app = Flask(__name__)

new_files = False

@app.route("/download/recurring", methods=['POST'])
@cross_origin()
def download_files():
    print("Downloading new files")
    # Creates a re-usable session object with your creds in-built
    github_session = requests.Session()
    github_session.auth = (secrets.username, secrets.github_token)

    # Downloading the csv file from your GitHub
    url = "https://raw.githubusercontent.com/elnathanau1/private-app-files/master/plex-recurring-downloads.csv"
    download = github_session.get(url).content

    df = pd.read_csv(io.StringIO(download.decode('utf-8')))

    for _, row in df.iterrows():
        params = ["season_url", "show_name", "season", "start_ep", "root_folder"]
        headers = {"X-API-SOURCE" : row["X-API-SOURCE"]}
        body = {}
        for param in params:
            body[param] = row[param]

        r = requests.post('http://localhost:9050/download/season', json = body, headers = headers)

    return "Success"


def scan_new_files():
    print("Plex scanning for new files")
    # check if theres any new files downloading
    r = requests.get('http://localhost:9050/download/status/all?status=DOWNLOADING')
    response = json.loads(r.text)
    if len(response['download_ids']) == 0:
        # make scan call
        url = 'http://%s:32400/library/sections/1/refresh?X-Plex-Token=%s' % (secrets.plex_ip, secrets.plex_token)
        requests.get(url)


def delete_old_optimizations():
    print("Deleting old optimizations")
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


scheduler = BackgroundScheduler()
scheduler.add_job(download_files, 'cron', hour='0,4', minute='0')
scheduler.add_job(scan_new_files, 'cron', hour='8', minute='0')
scheduler.add_job(delete_old_optimizations, 'cron', hour='6', minute='0')
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(use_reloader=False)
