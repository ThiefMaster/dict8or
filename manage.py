import sys

from flask import current_app
from flask.ext.script import Manager, Shell, Command, Option
from dict8or.app import make_app, celery, redis


class Server(Command):
    """Runs the Flask development server i.e. app.run()"""

    def get_options(self):
        return (
            Option('-H', '--host', default='127.0.0.1', help='host to listen on'),
            Option('-p', '--port', default=8000, type=int, help='port to listen on'),
            Option('--force-evalex', action='store_true',
                   help='Enable evalex (remote code execution) even when listening on a host that is not localhost.'),
            Option('-t', '--threaded', action='store_true', help='Use a thread for each request.'),
            Option('-r', '--reloader', action='store_true', help='Use the flask reloader.')
        )

    def handle(self, app, host, port, force_evalex, threaded, reloader):
        use_evalex = True
        if host not in ('::1', '127.0.0.1'):
            if force_evalex:
                print ' * Binding to non-loopback host with evalex enabled.'
                print ' * This means anyone with access to this app is able to execute arbitrary python code!'
            else:
                print ' * Binding to non-loopback host; disabling evalex.'
                use_evalex = False
        app.run(host=host, port=port, use_evalex=use_evalex, threaded=threaded, use_reloader=reloader)


def run_worker(concurrency='4', beat=False):
    """Runs the celery worker"""
    args = sys.argv[:1]
    args += ('-c', concurrency)
    if beat:
        args += ('-B', '-s', 'tmp/celerybeat-schedule')
    with make_app().app_context():
        celery.worker_main(args)


def _make_shell_context():
    ctx = {
        'redis': redis,
        'app': current_app,
        'celery': celery
    }
    for key, func in celery.tasks.iteritems():
        if not key.startswith('dict8or.tasks.'):
            continue
        ctx_key = '_'.join(key.split('.')[2:])
        ctx[ctx_key] = func
    return ctx


def main():
    manager = Manager(make_app(), with_default_commands=False)

    manager.command(run_worker)

    manager.add_command('shell', Shell(make_context=_make_shell_context))
    manager.add_command('run', Server())

    manager.run()


if __name__ == '__main__':
    main()
