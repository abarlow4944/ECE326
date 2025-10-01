from bottle import route, run, template, static_file, request
from collections import Counter

global_keyword_dict = Counter()

@route('/')
def index():
    """Home Page """
    return template('index')


@route('/static/<filepath:path>')
def server_static(filepath):
    """Serving static files """
    return static_file(filepath, root='./static')

@route('/', method="GET")
def formHandler():
    """Handle the form submission"""
    keywords = request.query.get('keywords')

    keyword_dict = Counter()
    if keywords:
        keyword_list = keywords.split()
        keyword_dict.update(keyword_list)
        global_keyword_dict.update(keyword_list)

    return template('index', keyword_dict = keyword_dict, top_20 = global_keyword_dict.most_common(20))


run(host='localhost', port=8080, debug=True, reloader=True)