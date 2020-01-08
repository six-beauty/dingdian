# coding=utf-8
import requests
from lxml import etree
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
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

        self.driver = None

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

        if not self.driver:
            self.driver = webdriver.PhantomJS()
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class='so_list bookcase']").is_displayed())  
        resp = self.driver.page_source
        html = etree.HTML(resp)

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

        if not self.driver:
            self.driver = webdriver.PhantomJS()
        #print('url:', 'https://www.23us.us'+url)
        chapter_url = 'https://www.23us.us'+url
        print(chapter_url)
        self.driver.get(chapter_url)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class='listmain']").is_displayed())  
        resp = self.driver.page_source

        html = etree.HTML(resp)
        with open('source.html', 'w') as f:
            f.write(resp)
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
        #resp = self.parse_url(url)

        if not self.driver:
            self.driver = webdriver.PhantomJS()
        article_url = 'https://www.23us.us'+url
        print(article_url)
        self.driver.get(article_url)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class='content']").is_displayed())  
        resp = self.driver.page_source

        html = etree.HTML(resp)
        content = html.xpath('//div[@class="content"]/div[@id="content"]/text()')
        print(content)
        if '<' in content[0] or '>' in content[0]:
            del content[0]
            #content[0] = content[0].replace('<', '&lt;')
            #content[0] = content[0].replace('>', '&gt;')
        return '<br>'.join([c.encode('utf-8').decode('utf-8') for c in content])


if __name__=='__main__':
    dd = DdSpider()
    #for i in dd.get_index_result('赘婿'):
    #    print(i)

    #for chapter in dd.get_chapter('/html/21/21740'):
    #    print(chapter)

    print(dd.get_article('/html/19/19916/7312084.html'))

