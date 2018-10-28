import base64
import json
import os

from threading import Thread
from time import sleep

import dpath
import requests

from requests import RequestException

from spotify_my_words.exceptions import GeneralError

SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_SEARCH_URL = 'https://api.spotify.com/v1/search'
HTTP_SUCCESS = 200
TIMEOUT_ERROR = 429


def request_from_spotify(cleaned, total_items):
    # Yes using global is completely disgusting and wrong, but in the interests of this short
    # exercise, turning the whole thing into a class might be a bit overkill. Don't hate me.
    # This is a simple list so that multiple threads have somewhere to write to in at a specific
    # index to maintain order.
    global playlist
    playlist = ['' for _ in range(total_items)]

    headers = {'Authorization': f'Bearer {_get_token()}'}

    threads = []
    for token, metadata in cleaned.items():
        request_params = {
            'q': f'{token}',
            'type': 'track',
            'offset': 0,
            'limit': 1,
        }
        thread = Thread(
            target=_parse_track_metadata, args=(headers, request_params, metadata, token))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return json.dumps(playlist)


def _get_token():
    headers = {'Authorization': f'Basic {_encode_secrets()}'}
    body = {'grant_type': 'client_credentials'}

    try:
        token_response = _post_to_spotify(SPOTIFY_TOKEN_URL, headers, body)
    except GeneralError:
        raise
    else:
        return json.loads(token_response.text).get('access_token')


def _encode_secrets():
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    return base64.b64encode(bytes(f'{client_id}:{client_secret}', encoding='utf-8')).decode('utf-8')


def _parse_track_metadata(track_header, request_params, metadata, token):
    names = []
    artists = []
    while len(names) < metadata.get('limit'):
        try:
            name, artist = _get_track_metadata(SPOTIFY_SEARCH_URL, track_header, request_params)
        except TimeoutError as err:
            time_out, *_ = err.args
            sleep(time_out)
        else:
            request_params['offset'] += 1
            if name.lower().startswith(token) and name not in names:
                names.append(name)
                artists.append(artist)

    for this_index, full_index in enumerate(metadata.get('indices')):
        track_details = f'{names[this_index]} - {artists[this_index]}'
        playlist[full_index] = track_details

    return True


def _get_track_metadata(url, track_header, request_params):
    try:
        response = json.loads(_get_from_spotify(url, track_header, request_params).text)
    except (GeneralError, TimeoutError):
        raise
    else:
        items = response.get('tracks').get('items')
        name = dpath.get(items, '*/name')
        artists = dpath.values(items, '*/artists/*/name')
        artists = ', '.join(artists) if len(artists) > 1 else str(next(iter(artists)))

        return name, artists


def _post_to_spotify(url, headers, data):
    try:
        response = requests.post(url, headers=headers, data=data, verify=True)
        if response.status_code != HTTP_SUCCESS:
            raise RequestException
    except RequestException as exc:
        raise GeneralError(f'Unable to send information to API: {exc}')
    else:
        return response


def _get_from_spotify(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params, verify=True)
        if response.status_code == TIMEOUT_ERROR:
            sleep_time = int(response.headers._store.get('retry-after')[1])
            raise TimeoutError(sleep_time)
        if response.status_code != HTTP_SUCCESS:
            raise RequestException
    except RequestException as exc:
        raise GeneralError(f'Unable to get information from API: {exc}')
    else:
        return response
