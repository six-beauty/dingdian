# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError
import urllib.parse
try:
    import pinyin
except:
    from ..spider import pinyin


"""
爬虫api：
    搜索结果页：get_index_result(search)
    小说章节页：get_chapter(url)
    章节内容：get_article(url)
"""
class DdSpider(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
        }


    def parse_url(self, url, verify=True):
        try:
            resp = requests.get('https://www.23us.us'+url, headers=self.headers, verify=verify)
            if resp.status_code == 200:
                # 处理一下网站打印出来中文乱码的问题
                resp.encoding = 'utf-8'
                return resp.text
            return None
        except ConnectionError:
            print('Error.')
        return None

    # 搜索结果页数据
    def get_index_result(self, search):
        #请求url
        data = {'ie':'utf8', 'q':search}
        url = 'https://www.23us.us/s.php?'+urllib.parse.urlencode(data)

        r = requests.get(url)
        html = etree.HTML(r.text)

        titles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/h4[@class="bookname"]/a/text()')
        urls = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/h4[@class="bookname"]/a/@href')

        images = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookimg"]/a/img/@src')
        authors = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="author"]/text()')
        # 简介
        profiles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/p/text()')

        styles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="cat"]/text()')
        states = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="update"]/a/text()')

        for title, url, image, author, profile, style, state in zip(titles, urls, images,  
                authors, profiles, styles, states):

            title = title.encode('utf-8').decode('utf-8').strip()
            author = author.encode('utf-8').decode('utf-8').strip()
            profile = profile.encode('utf-8').decode('utf-8').strip()
            author = author.encode('utf-8').decode('utf-8').strip()
            pinyin_title = pinyin.convert_to_lazy_pinyin(title)

            # 简介profiles
            url = url[:-1] if url.endswith('/') else url

            data = {
                'title': title,
                'url': url,
                'image': 'https://www.23us.us'+image,
                'author': author.strip(),
                'profile': profile.strip().replace('\u3000', '').replace('\n', ''),
                'style': style[3:],
                'state': state,
            }
            yield data

    # 小说章节页数据
    def get_chapter(self, url):
        #resp = self.parse_url(url)

        chapter_url = 'https://www.23us.us'+url
        print(chapter_url)
        r = requests.get(chapter_url)

        html = etree.HTML(r.text)
        with open('source.html', 'w') as f:
            f.write(r.text)
        chapters = html.xpath('//div[@class="listmain"]/dl/dd/a/text()')
        urls = html.xpath('//div[@class="listmain"]/dl/dd/a/@href')
        for chapter_url, chapter in zip(urls, chapters):
            data = {
                'url': chapter_url,
                'chapter': chapter.encode('utf-8').decode('utf-8'),
            }
            yield data

    # 章节内容页数据
    def get_article(self, url):
        article_url = 'https://www.23us.us'+url
        r = requests.get(article_url, timeout=10)

        html = etree.HTML(r.text)
        #with open('article.html', 'w') as f:
        #    f.write(r.text)

        content = html.xpath('//div[@class="content"]/div[@class="showtxt"]/text()')
        print(content)
        if '<' in content[0] or '>' in content[0]:
            del content[0]
            #content[0] = content[0].replace('<', '&lt;')
            #content[0] = content[0].replace('>', '&gt;')
        return '<br>'.join([c.encode('utf-8').decode('utf-8') for c in content])


if __name__=='__main__':
    dd = DdSpider()
    #for i in dd.get_index_result('覆手'):
    #    print(i)

    #for chapter in dd.get_chapter('/html/32/32187'):
    #    print(chapter)

    #https://www.23us.us/html/32/32187/22363195.html
    print(dd.get_article('/html/32/32187/22363195.html'))


    #with open('article.html', 'r') as f:
    #    r_text = f.read()
    #html = etree.HTML(r_text)

    #content = html.xpath('//div[@class="content"]/div[@class="showtxt"]/text()')
    #if '<' in content[0] or '>' in content[0]:
    #    del content[0]
    #    #content[0] = content[0].replace('<', '&lt;')
    #    #content[0] = content[0].replace('>', '&gt;')
    #print('<br>'.join([c.encode('utf-8').decode('utf-8') for c in content]))
