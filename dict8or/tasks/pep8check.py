from collections import defaultdict

from pep8 import StyleGuide, BaseReport
from flask import json

from dict8or.app import celery, redis


class Dict8orReport(BaseReport):
    def __init__(self, options):
        super(Dict8orReport, self).__init__(options)
        self.history = defaultdict(list)

    def error(self, line_number, offset, text, check):
        super(Dict8orReport, self).error(line_number, offset, text, check)
        self.history[self.filename].append({'line': line_number, 'code': text[:4]})


@celery.task
def pep8_check(pkg_name, dir_path):
    print("Scanning {}".format(dir_path))

    sg = StyleGuide(reporter=Dict8orReport)
    r = sg.check_files([dir_path])

    n_warn = r.get_count('W')
    n_err = r.get_count('E')

    redis.hmset('pkg:' + pkg_name, {
        'details': json.dumps(r.history),
        'warnings': n_warn,
        'errors': n_err
    })
    redis.zadd('ranking', n_err * 2 + n_warn, pkg_name)
    print("Done!")
