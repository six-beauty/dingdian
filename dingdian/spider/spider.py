# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError


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
        if page == 0:
            url = 'http://zhannei.baidu.com/cse/search?q={search}&s=6445266503022880974&srt=def&nsid=0'.format(search=search)
        else:
            url = 'http://zhannei.baidu.com/cse/search?q={search}&s=6445266503022880974&srt=def&nsid={page}'.format(search=search, page=page)
        resp = self.parse_url(url)
        html = etree.HTML(resp)
        titles = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/h3/a/@title')
        urls  = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/h3/a/@href')

        images = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-pic"]/a/img/@src')
        profiles = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/p[@class="result-game-item-desc"]/text()')
        authors = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/div[@class="result-game-item-info"]/p[1]/span[2]/text()')
        styles = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/div[@class="result-game-item-info"]/p[2]/span[2]/text()')
        states = html.xpath('//div[@class="result-item result-game-item"]//div[@class="result-game-item-detail"]/div[@class="result-game-item-info"]/p[3]/span[2]/text()')
        for title, url, image, author, profile, style, state in zip(titles, urls, images, authors, profiles, styles,
                                                                  states):
            data = {
                'title': title.strip(),
                'url': url,
                'image': image,
                'author': author.strip(),
                'profile': profile.strip().replace('\u3000', '').replace('\n', ''),
                'style': style.strip(),
                'state': state.strip()
            }
            yield data

    # 小说章节页数据
    def get_chapter(self, url):
        resp = self.parse_url(url)
        html = etree.HTML(resp)
        chapters = html.xpath('//*[@class="listmain"]/dl/dd/a/text()')
        urls = html.xpath('//*[@class="listmain"]/dl/dd/a/@href')

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
        return '<br>'.join(content)


#dd = DdSpider()
'''
for i in dd.get_index_result('赘婿',page=0):
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
