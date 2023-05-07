from flask import Flask, request, redirect, jsonify
import hashlib
import os
import re

app = Flask(__name__)

url_map = {}

@app.route('/convert', methods=['GET'])
def convert_long_url_to_short():
    url = request.args.get('url')
    # validate that the input URL is valid
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,63}|[A-Z0-9-]{2,63})|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/[\w~!$&\'()*+,;=:@.-]+)*', re.IGNORECASE)  # path and query string
    if not re.match(url_regex, url):
        return '400 Bad Request - Invalid URL', 400
    # generate a short URL using MD5 hashing and base62 encoding
    md5_hash = hashlib.md5(url.encode()).digest()
    base62_alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base62 = ''
    for b in md5_hash:
        base62 += base62_alphabet[b % 62]
    short_url = f'https://{request.host}/{base62}'
    url_map[base62] = url
    json_data = {
        'long_url': url,
        'short_url': short_url,
    }
    return jsonify(json_data)

@app.route('/<short_url>', methods=['GET'])
def redirect_to_long_url(short_url):
    long_url = url_map.get(short_url)
    if long_url is None:
        return '404 Not Found', 404
    return redirect(long_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
