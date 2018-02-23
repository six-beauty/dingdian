from flask import flash, render_template, url_for, redirect, request, current_app, jsonify
from flask.blueprints import Blueprint

from dingdian import db
from .forms import SearchForm
from ..spider.spider import DdSpider
from ..models import Novel, Chapter, Article


main = Blueprint('main', __name__)

@main.errorhandler(404)
def page_not_found(error):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search_name.data
        flash('搜索成功。')
        return redirect(url_for('main.result', search=search))
    return render_template('index.html', form=form)

@main.route('/results/<search>')
def result(search):
    page = request.args.get('page', 0, type=int)
    # 查找数据库中search键相等的结果，如果有则不需要调用爬虫，直接返回
    books = Novel.query.filter_by(search_name=search, page=page).all()
    if books:
        return render_template('result.html', search=search, page=page, books=books)

    spider = DdSpider()

    for data in spider.get_index_result(search, page):
        novel = Novel(book_name=data['title'],
                      book_url=data['url'],
                      book_img=data['image'],
                      author=data['author'],
                      style=data['style'],
                      profile=data['profile'],
                      last_update=data['time'],
                      page=page,
                      search_name=search)
        db.session.add(novel)
    books = Novel.query.filter_by(search_name=search, page=page).all()
    return render_template('result.html', search=search, page=page, books=books)

@main.route('/chapter/<int:book_id>')
def chapter(book_id):
    page = request.args.get('page', 1, type=int)
    desc = request.args.get('desc', 0, type=int)
    if desc == 0:
        chapter_order = Chapter.chapter_id.asc()
    else:
        chapter_order = Chapter.chapter_id.desc()

    last_chapter = db.session.query(Chapter.chapter_id).filter_by(book_id=book_id).order_by(Chapter.chapter_id.desc()).first()
    book = Novel.query.filter_by(id=book_id).first()
    if last_chapter:
        #last page, spider try again
        pagination = db.session.query(Chapter).filter_by(book_id=book_id).order_by(chapter_order).paginate(
            page, per_page=current_app.config['CHAPTER_PER_PAGE'],
            error_out=False
        )

        if not pagination.has_next:
            chapter_dict = {}

            spider = DdSpider()
            for data in spider.get_chapter(book.book_url):
                chapter_id = int(data['url'].split('/')[-1].split('.')[0])
                if chapter_id <= last_chapter.chapter_id:
                    continue
                #sort by chapter_id
                chapter_dict[chapter_id] = {'book_id':book_id, 'chapter_id':chapter_id, 'chapter':data['chapter'], 'chapter_url':data['url']}

            for chapter_id in sorted(chapter_dict.keys()):
                data = chapter_dict[chapter_id]
                db.session.execute(Chapter.__table__.insert().prefix_with('IGNORE'), data)
            if len(chapter_dict) > 0 :
                db.session.commit()
                pagination = db.session.query(Chapter).filter_by(book_id=book_id).order_by(chapter_order).paginate(
                    page, per_page=current_app.config['CHAPTER_PER_PAGE'],
                    error_out=False
                )
        chapters = pagination.items
        return render_template('chapter.html', book=book, chapters=chapters, pagination=pagination, desc=desc)

    #spider
    spider = DdSpider()
    chapter_dict = {}
    for data in spider.get_chapter(book.book_url):
        chapter_id = data['url'].split('/')[-1].split('.')[0]
        #sort by chapter_id
        chapter_dict[chapter_id] = {'book_id':book_id, 'chapter_id':chapter_id, 'chapter':data['chapter'], 'chapter_url':data['url']}

    for chapter_id in sorted(chapter_dict.keys()):
        data = chapter_dict[chapter_id]
        db.session.execute(Chapter.__table__.insert().prefix_with('IGNORE'), data)
    db.session.commit()

    pagination2 = db.session.query(Chapter).filter_by(book_id=book_id).order_by(chapter_order).paginate(
        page, per_page=current_app.config['CHAPTER_PER_PAGE'],
        error_out=False
    )
    chapters = pagination2.items

    return render_template('chapter.html', book=book, chapters=chapters, pagination=pagination2, desc=desc)

@main.route('/content/<int:chapter_id>')
def content(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    article = Article.query.filter_by(chapter_id=chapter_id).first()
    if article:
        #需要更新
        if '正在手打中' in article.content or '内容更新后' in article.content:
            spider = DdSpider()
            cont2 = spider.get_article(chapter.chapter_url)
            if not '正在手打中，请稍等片刻，内容更新后，需要重新刷新页面' in cont2 or article.content!=cont2:
                article.content = cont2
                db.session.commit()

        chapter = Chapter.query.filter_by(id=chapter_id).first()
        return render_template('article.html', chapter=chapter, article=article, book_id=chapter.book_id)

    spider = DdSpider()
    article2 = Article(content=spider.get_article(chapter.chapter_url),
                      chapter_id=chapter_id)
    db.session.add(article2)
    return render_template('article.html', chapter=chapter, article=article2, book_id=chapter.book_id)

# 下一章
@main.route('/next/<int:chapter_id>')
def next(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    book = Novel.query.filter_by(id=chapter.book_id).first()
    all_chapters = [i for i in book.chapters]
    # all_chapters是一个集合,通过操作数组很容易拿到下一章内容
    if all_chapters[-1] != chapter:
        next_chapter = all_chapters[all_chapters.index(chapter)+1]
        return redirect(url_for('main.content', chapter_id=next_chapter.id))
    else:
        chapter_dict = {}
        spider = DdSpider()
        print('--next chapter_id:%s'%chapter.chapter_id)
        for data in spider.get_chapter(book.book_url):
            chapid = int(data['url'].split('/')[-1].split('.')[0])
            if chapid <= chapter.chapter_id:
                continue
            print('new chapter:%s'%chapid)
            #sort by chapter_id
            chapter_dict[chapid] = {'book_id':chapter.book_id, 'chapter_id':chapid, 'chapter':data['chapter'], 'chapter_url':data['url']}

        for chapid in sorted(chapter_dict.keys()):
            data = chapter_dict[chapid]
            db.session.execute(Chapter.__table__.insert().prefix_with('IGNORE'), data)
        db.session.commit()

        #没有更新
        if len(chapter_dict) == 0 :
            flash('已是最后一章了。')
            return redirect(url_for('main.content', chapter_id=chapter_id))

    return next(chapter_id)


@main.route('/prev/<int:chapter_id>')
def prev(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    book = Novel.query.filter_by(id=chapter.book_id).first()
    all_chapters = [i for i in book.chapters]
    if all_chapters[0] != chapter:
        prev_chapter = all_chapters[all_chapters.index(chapter)-1]
        return redirect(url_for('main.content', chapter_id=prev_chapter.id))
    else:
        flash('没有上一章了哦。')
        return redirect(url_for('main.content', chapter_id=chapter_id))

