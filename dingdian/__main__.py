# coding=utf-8

import argparse
import logging
import logging.handlers
import sys
import dingdian
import gevent.wsgi
import os
import textwrap
import typing

db = dingdian.db

def main():
    log_dir = '%s/log/dingdian'%os.environ['HOME']
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(level=logging.INFO,
        format='[%(asctime)s %(name)-12s %(levelname)-s] %(message)s',
        datefmt='%m-%d %H:%M:%S',
        #filename=time.strftime('log/dump_analyze.log'),
        filemode='a')
    htimed = logging.handlers.TimedRotatingFileHandler("%s/dingdian.log"%(log_dir), 'D', 1, 0)
    htimed.suffix = "%Y%m%d-%H%M"
    htimed.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(name)-12s %(levelname)-s] %(message)s', datefmt='%m-%d %H:%M:%S')
    htimed.setFormatter(formatter)
    #day time split log file
    logging.getLogger('').addHandler(htimed)

    arguments = parse_args()

    app = dingdian.create_app()
    app.logger.addHandler(htimed)
    app.arguments = arguments

    if arguments.manage == 'run':
        try:
            http_server = gevent.wsgi.WSGIServer((arguments.host, arguments.port), app, log=app.logger)
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass

    elif arguments.manage == 'init':
        with app.app_context():
            #db init
            db.create_all()
            db.session.commit()
    elif arguments.manage == 'clear':
        with app.app_context():
            from dingdian.models import Alembic, Novel, Chapter, Article
            
            # 清空数据库
            alembics = Alembic.query.all()
            for s in alembics:
                db.session.delete(s)
            novels = Novel.query.all()
            for n in novels:
                db.session.delete(n)
            chapters = Chapter.query.all()
            for c in chapters:
                db.session.delete(c)
            articles = Article.query.all()
            for a in articles:
                db.session.delete(a)

            db.session.commit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lightweight web interface for dingdian.",
        epilog=textwrap.dedent("""\
                Copyright (C) 2017  cw lyn ALPER <http://blog.leanote.com/sanyue9394@163.com>
        """),
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--host", action="store", type=str, required=False, default="0.0.0.0",
        help="the host address dingdian web server should listen on"
    )
    parser.add_argument(
        "--port", action="store", type=int, required=True,
        help="the port number dingdian web server should listen on"
    )

    parser.add_argument(
        "--manage", action="store", type=str, required=False, default = "run",
        help="choose run/init/clear, dingdian web server should do"
    )

    return parser.parse_args(sys.argv[1:])

if __name__ == "__main__":                                                                                                                            
    sys.exit(main())

