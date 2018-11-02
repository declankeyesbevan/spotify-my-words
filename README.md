# Spotify my Words
Yo dawg we heard you like songs so we got you to send us some letters to get back a playlist.

## About
Dev challenge for a job application which tests API creation and consumption.

Send a query string of letters and you will get back a playlist of songs from Spotify which start
with the same letters. For example if your query string is `cool` you could get back:

    "Chinook - Dakota",
    "Open Your Eyes - Remastered - Nalin & Kane",
    "Old Skin - Ólafur Arnalds ft. Arnór Dan,
    "Loreley - Kölsch",

## Requires

    python3.6

## Prerequisites
A [Spotify developer account](https://developer.spotify.com) and a
[registered app](https://developer.spotify.com/documentation/general/guides/app-settings).

From there store your client ID and client secret into the following environment variables:

    CLIENT_ID
    CLIENT_SECRET

You may also wish to add a certificate to avoid insecure connection warnings to the Spotify API. I
use the Python library `certifi` for this.

## Installation

    git clone https://github.com/declankeyesbevan/spotify-my-words.git
    cd spotify-my-words
    pip3 install virtualenv
    virtualenv env
    . env/bin/activate
    pip install -r requirements.txt
    export PYTHONPATH=`pwd`

## Run
Start the Flask app from the runner.

    chmod a+x run_my_dawg.py
    python run_my_dawg.py

## Usage
Using your HTTP tool of choice (I like Postman, but you can use a browser) send a `GET` to
`localhost` with a query string like the following:

    http://0.0.0.0:5000/secretmsg?msg=cooly/ 56b>'"@ HDasj4952304[]`6hdch

Anything that is not a letter will be ignored and what is left will be lower-cased so this will
resolve to `coolybhdasjhdch`. Anything longer than 30 valid characters will also be ignored. 

Or if you like the command-line:

    curl -X get http://0.0.0.0:5000/secretmsg?msg=coolmessagebro
