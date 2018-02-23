#!/usr/bin/env python
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from dingdian import db
from dingdian import create_app
import logging
import logging.handlers


app = create_app(os.getenv('CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    from flask_migrate import upgrade
    # 情况数据库的操作只在运行过后才可以取消注释使用
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

if __name__ == '__main__':
    log_dir = '%s/log/dingdian'%os.environ['HOME']
    #log_dir = '/home/sany/log/dingdian'
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
    logging.info("dingdian started")

    manager.run()
