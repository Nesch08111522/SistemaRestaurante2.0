from html.parser import HTMLParser
from pathlib import Path

from tests.test_qa_regression import app


class Stylesheets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.head_styles = []

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        attrs = dict(attrs)
        if self.in_head and tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.head_styles.append(attrs.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False


def test_discovery_renders_maplibre_styles_in_inherited_head(app):
    response = app.test_client().get('/descubrir/')
    assert response.status_code == 200
    parser = Stylesheets()
    parser.feed(response.text)
    links = [url for url in parser.head_styles if 'vendor/maplibre/maplibre-gl.css' in url]
    assert len(links) == 1
    css = app.test_client().get(links[0])
    assert css.status_code == 200
    assert '.maplibregl-marker{left:0;position:absolute;top:0;' in css.text
