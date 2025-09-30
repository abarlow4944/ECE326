from bottle import route, run, template, static_file

@route('/')
def hello():
    return template('index')


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


run(host='localhost', port=8080, debug=True)