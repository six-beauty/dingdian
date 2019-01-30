# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError
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

    def parse_url(self, url):
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                # 处理一下网站打印出来中文乱码的问题
                resp.encoding = 'utf-8'
                return resp.text
            return None
        except ConnectionError:
            print('Error.')
        return None

    # 搜索结果页数据
    def get_index_result(self, search, page=0):
        #请求url
        url = 'https://sou.xanbhx.com/search?siteid=qula&q={search}'.format(search=search)
        resp = self.parse_url(url)
        html = etree.HTML(resp)

        titles = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s2"]/a/text()')
        urls = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s2"]/a/@href')
        #images = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s2"]/a/@href')
        authors = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s4"]/text()')
        # 简介
        #profiles  = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s2"]/a/@href')
        times = html.xpath('//div[@class="search-list"]/ul/li/span[@class="s6"]/text()')
        styles= html.xpath('//div[@class="search-list"]/ul/li/span[@class="s1"]/text()')
        states= html.xpath('//div[@class="search-list"]/ul/li/span[@class="s7"]/text()')

        for title, url, author, style, state in zip(titles, urls, 
                authors, styles, states):
            title = title.strip()
            pinyin_title = pinyin.convert_to_lazy_pinyin(title)

            # 简介profiles
            url = url[:-1] if url.endswith('/') else url
            resp = self.parse_url(url)
            html = etree.HTML(resp)
            profile = html.xpath('//div[@id="maininfo"]/div[@id="intro"]/text()')[0]

            data = {
                'title': title,
                'url': url,
                'image': "https://www.qu.la/BookFiles/BookImages/%s.jpg"%(pinyin_title),
                'author': author.strip(),
                'profile': profile.strip().replace('\u3000', '').replace('\n', ''),
                'style': style.strip(),
                'state': state.strip()
            }
            yield data

    # 小说章节页数据
    def get_chapter(self, url):
        url = url[:-1] if url.endswith('/') else url
        resp = self.parse_url(url)
        html = etree.HTML(resp)
        chapters = html.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/text()')
        urls = html.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')

        url = url.replace('index.html', '')
        for chapter_url, chapter in zip(urls, chapters):
            data = {
                'url': url + chapter_url,
                'chapter': chapter
            }
            yield data

    # 章节内容页数据
    def get_article(self, url):
        resp = self.parse_url(url)
        html = etree.HTML(resp)
        content = html.xpath('//*[@id="content"]/text()')
        if '<' in content[0] or '>' in content[0]:
            del content[0]
            #content[0] = content[0].replace('<', '&lt;')
            #content[0] = content[0].replace('>', '&gt;')
        content = [text.replace('\u3000', '') for text in content]
        return '<br>'.join(content)



#dd = DdSpider()
'''
for i in dd.get_index_result('赘婿'):
    print(i)
'''
#url='http://www.shuquge.com/txt/73808/17088548.html'
#print(dd.get_article(url))

'''
url = 'http://www.shuquge.com/txt/4833/index.html'
chapter_dict={}
for data in dd.get_chapter(url):
    chapter_id = int(data['url'].split('/')[-1].split('.')[0])
    #sort by chapter_id
    chapter_dict[chapter_id] = {'chapter_id':chapter_id, 'chapter':data['chapter'], 'chapter_url':data['url']}

for chapter_id in sorted(chapter_dict.keys()):
    print(chapter_id)
'''
