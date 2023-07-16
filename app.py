import requests
from flask import Flask, request, render_template, Response
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    base_url = request.args.get('url')
    user_agent = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'

    headers = {
        'User-Agent': user_agent,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'DNT': '1',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1'
    }
    session = requests.Session()
    session.cookies.clear()
    response = session.get(base_url, headers=headers)

    # Parsing the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Rewrite URLs in the HTML content to go through the proxy
    for link in soup.find_all('a'):
        if link.get('href'):
            link['href'] = urljoin(base_url, link['href'])

    # Rewrite URLs in the HTML content for stylesheets to go through the proxy
    for style in soup.find_all('link', rel="stylesheet"):
        if style.get('href'):
            style['href'] = urljoin(base_url, style['href'])

    # Rewrite URLs in the HTML content for scripts to go through the proxy
    for script in soup.find_all('script', src=True):
        script_url = script['src']
        
        # Exclude URLs that match a specific pattern to prevent endless loop or unwanted behavior
        if not re.match(r'^http(s)?:\/\/localhost(:\d+)?\/proxy\?', script_url):
            script['src'] = urljoin(base_url, script_url)

    # Return the modified HTML response
    modified_response = Response(soup.prettify(), content_type='text/html')
    return modified_response

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
