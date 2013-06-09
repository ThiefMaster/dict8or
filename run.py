import argparse

from dict8or.app import make_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', metavar='IP', help='Host (default: 127.0.0.1)')
    parser.add_argument('--port', default=8000, type=int, metavar='PORT', help='Port (default: 8000)')
    parser.add_argument('-e', '--evalex', help='Enable code execution in the debugger', action='store_true')
    parser.add_argument('-r', '--reloader', help='Use the flask autoreloader', action='store_true')
    args = parser.parse_args()
    app = make_app()
    app.run(args.host, args.port, debug=app.debug, use_reloader=args.reloader, use_evalex=args.evalex)


if __name__ == '__main__':
    main()