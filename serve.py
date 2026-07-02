import functools
from http.server import HTTPServer, SimpleHTTPRequestHandler

DIRECTORY = "/Users/fabianherrera/Desktop/FabDev/augurio"
Handler = functools.partial(SimpleHTTPRequestHandler, directory=DIRECTORY)
HTTPServer(("127.0.0.1", 4321), Handler).serve_forever()
