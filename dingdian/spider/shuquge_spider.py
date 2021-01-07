# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError
import urllib.parse

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
    def get_index_result(self, search):
        #请求url
        data = {'searchkey':search}
        url = 'http://www.shuquge.com/search.php?'+urllib.parse.urlencode(data)

        resp = self.parse_url(url)
        html = etree.HTML(resp)

        titles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/h4[@class="bookname"]/a/text()')
        urls = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/h4[@class="bookname"]/a/@href')

        #images = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookimg"]/a/img/@src')
        authors = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="author"]/text()')
        # 简介
        #profiles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/p/text()')

        styles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="cat"]/text()')
        states = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="update"]/a/text()')

        for title, url, author, style, state in zip(titles, urls, authors, styles, states):

            # 简介profiles
            url = url[:-1] if url.endswith('/') else url 

            data = {
                'title': title,
                'url': 'http://www.shuquge.com'+ url ,
                'image': '',
                'author': author.strip(),
                'profile': '',
                'style': style[3:],
                'state': state,
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
        print(url, len(content))
        if len(content) == 0:
            with open('1.html', 'w') as f:
                f.write(resp.text)
        if '<' in content[0] or '>' in content[0]:
            del content[0]
            #content[0] = content[0].replace('<', '&lt;')
            #content[0] = content[0].replace('>', '&gt;')
        return '<br>'.join(content)

if __name__=='__main__':
    dd = DdSpider()
    for i in dd.get_index_result('赘婿'):
        print(i)

    #url='http://www.shuquge.com/txt/4833/30735718.html'
    #print(dd.get_article(url))

    '''
    url = 'http://www.shuquge.com/txt/4833/index.html'
    chapter_dict={}
    for data in dd.get_chapter(url):
        chapter_id = int(data['url'].split('/')[-1].split('.')[0])
        #sort by chapter_id
        chapter_dict[chapter_id] = {'chapter_id':chapter_id, 'chapter':data['chapter'], 'chapter_url':data['url']}

    for chapter_id in sorted(chapter_dict.keys()):
        print(chapter_id, chapter_dict[chapter_id])
    '''
