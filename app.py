import pandas as pd
import requests
import io
import json
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import secrets

app = Flask(__name__)

new_files = False

def download_files():
    print("Running download_files")
    # Creates a re-usable session object with your creds in-built
    github_session = requests.Session()
    github_session.auth = (secrets.username, secrets.token)

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
        print(body)

        r = requests.post('http://localhost:9050/download/season', json = body, headers = headers)
        print(r.text)
        # if len(response_json['download_ids']) != 0:
        #     new_files = True


scheduler = BackgroundScheduler()
scheduler.add_job(download_files, 'cron', hour='2', minute='0')
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(use_reloader=False)
