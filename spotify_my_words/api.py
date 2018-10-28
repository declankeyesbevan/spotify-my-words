import flask

from flask import request, Response

from spotify_my_words.exceptions import GeneralError
from spotify_my_words.parser import parse_message
from spotify_my_words.requester import request_from_spotify

app = flask.Flask(__name__)

HTTP_SUCCESS = 200
INTERNAL_SERVER_ERROR = 500


@app.route('/secretmsg', methods=['GET'])
def get_message():
    message = request.args.get('msg')

    try:
        cleaned, total_items = parse_message(message)
        playlist = request_from_spotify(cleaned, total_items)
    except GeneralError as exc:
        return Response(exc, status=INTERNAL_SERVER_ERROR, mimetype='application/json')
    else:
        return Response(playlist, status=HTTP_SUCCESS, mimetype='application/json')
