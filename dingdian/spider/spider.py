# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError
import urllib.parse

def save_html(resp):
    with open('1.html', 'w') as f:
        f.write(resp)

def read_html():
    with open('1.html', 'r') as f:
        return f.read()

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
        data = {'q':search}
        url = 'http://www.x23us.us/modules/article/search.php?'+urllib.parse.urlencode(data)

        resp = self.parse_url(url)
        #save_html(resp)
        #resp = read_html()
        html = etree.HTML(resp)

        titles = html.xpath('//table[@class="grid"]/tr[@id="nr"]/td[@class="odd"]/a/text()')
        urls = html.xpath('//table[@class="grid"]/tr[@id="nr"]/td[@class="odd"]/a/@href')
        #images = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookimg"]/a/img/@src')
        authors = html.xpath('//table[@class="grid"]/tr[@id="nr"]/td[@class="odd"]/text()')
        authors = [authors[_id] for _id in range(len(authors)) if _id%2==0 ]
        # 简介
        profiles = html.xpath('//table[@class="grid"]/tr[@id="nr"]/td[@class="even"]/a/text()')
        #styles = html.xpath('//div[@class="bookbox"]/div[@class="p10"]/div[@class="bookinfo"]/div[@class="cat"]/text()')
        states = html.xpath('//table[@class="grid"]/tr[@id="nr"]/td[@class="even"][@align="center"]/text()')

        for title, url, author, profile, state in zip(titles, urls, authors, profiles, states):

            # 简介profiles
            url = url[:-1] if url.endswith('/') else url 

            data = {
                'title': title,
                'url': url ,
                'image': '',
                'author': author.strip(),
                'profile': profile,
                'style': '',
                'state': state,
            }
            yield data


    # 小说章节页数据
    def get_chapter(self, url):
        resp = self.parse_url(url)

        print(url)
        html = etree.HTML(resp)
        chapters = html.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/text()')
        urls = html.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')

        url = url.replace('index.html', '')
        for chapter_url, chapter in zip(urls, chapters):
            data = {
                'url': 'http://www.x23us.us' + chapter_url,
                'chapter': chapter
            }
            yield data

    # 章节内容页数据
    def get_article(self, url):
        resp = self.parse_url(url)
        html = etree.HTML(resp)
        content = html.xpath('//*[@id="content"]/text()')
        if len(content) == 0:
            with open('1.html', 'w') as f:
                f.write(resp)
        if '<' in content[0] or '>' in content[0]:
            del content[0]
            #content[0] = content[0].replace('<', '&lt;')
            #content[0] = content[0].replace('>', '&gt;')
        return '<br>'.join(content)


if __name__=='__main__':
    dd = DdSpider()
    for i in dd.get_index_result('赘婿'):
        print(i)

    #url = 'http://www.x23us.us/72_72292/34200559.html'
    #print(dd.get_article(url))

    '''
    url='http://www.x23us.us/72_72292/'
    chapter_dict={}
    for data in dd.get_chapter(url):
        chapter_id = int(data['url'].split('/')[-1].split('.')[0])
        #sort by chapter_id
        chapter_dict[chapter_id] = {'chapter_id':chapter_id, 'chapter':data['chapter'], 'chapter_url':data['url']}

    for chapter_id in sorted(chapter_dict.keys()):
        print(chapter_id, chapter_dict[chapter_id])
    '''
