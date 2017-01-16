import requests
from bs4 import BeautifulSoup

from Lib.Currency.ThreadingPool import ThreadingPool
from Lib.NetCrawl.HtmlAnalyse import HtmlAnalyse
from Lib.NetCrawl.Proxy_Pool import ProxyPool
from OneCategoryTest.oracleSave import OracleSave


class Category:
    def __init__(self):
        self.proxy_pool = ProxyPool()

    def get_categories(self):
        main_url = "http://www.chip1stop.com/web/CHN/zh/category/interconnects/"
        self.proxy_ip = self.proxy_pool.get()
        while True:
            try:
                html_analsye = HtmlAnalyse(main_url, proxy=self.proxy_ip)
                bs_content = html_analsye.get_bs_contents()
                break
            except Exception as e:
                print(e)
                self.proxy_pool.remove(self.proxy_ip)
                self.proxy_ip = self.proxy_pool.get()

        ul_tags = bs_content.find_all(name="ul", attrs={"class": "tabTop_list"})

        categories = []
        for ul_tag in ul_tags:
            a_tags = ul_tag.find_all(name="a")
            for a_tag in a_tags:
                category_url = a_tag.get("href")
                category_name = a_tag.text
                category = (category_name, category_url)
                categories.append(category)
        return categories





    def get_product_list(self):
        categories = self.get_categories()

        # def thread_go(page_no):


        for category in categories:
            category_name, category_url = category

            form_data = {
                "nextSearchIndex": "0",
                "dispPageNo": "1",
                "dispNum": "100",
                "type": "page"
            }
            request_headers = {
                "Accept": "text/html, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://www.chip1stop.com",
                "Host": "www.chip1stop.com",
                "Proxy-Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.14 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }
            my_session = requests.session()
            my_session.headers.update(request_headers)
            self.proxy_ip = self.proxy_pool.get()
            while True:
                try:
                    res = my_session.post(category_url, data=form_data, proxies=self.proxy_ip, timeout=10)
                    print(res.status_code)
                    if res.status_code == 200:
                        break
                    self.proxy_pool.remove(self.proxy_ip)
                    self.proxy_ip = self.proxy_pool.get()
                except Exception as e:
                    print(e)
                    self.proxy_pool.remove(self.proxy_ip)
                    self.proxy_ip = self.proxy_pool.get()
            content = res.content.decode()
            bs_content = BeautifulSoup(content, "lxml")
            products_count = bs_content.find(name="span", attrs={"class": "bold_red"}).text.replace(",", "").replace(
                "件", "")
            pages_count = int(int(products_count) / 25) + 1

            if pages_count > 401:
                pages_count = 401

            for page_no in range(1, pages_count + 1):
                print("Page:", page_no)
                complete_form_data = {
                    "nextSearchIndex": "0",
                    "dispPageNo": "1",
                    "dispNum": "25",
                    "rental": "false",
                    "partSameFlg": "false",
                    "subWinSearchFlg": "false",
                    "used": "false",
                    "newProductFlg": "false",
                    "newProudctHandlingFlg": "false",
                    "newSameDayShippedFlg": "false",
                    "eventId": "0001",
                    "searchType": "2",
                    "dispAllFlg": "true",
                }
                page_parts = range(0, 25, 5)
                for page_part in page_parts:
                    print("Part:", page_part)
                    # def thread_go(page_part):
                    complete_form_data['nextSearchIndex'] = page_part
                    complete_form_data['dispPageNo'] = page_no
                    complete_form_data['type'] = "page"
                    while True:
                        try:
                            detail_url = category_url + "&dispPageNo=%d" % page_no
                            res = my_session.post(detail_url, data=complete_form_data, proxies=self.proxy_ip,
                                                  timeout=20)
                            print(res.status_code)
                            if res.status_code == 200:
                                break
                            self.proxy_pool.remove(self.proxy_ip)
                            self.proxy_ip = self.proxy_pool.get()
                        except Exception as e:
                            print(e)
                            self.proxy_pool.remove(self.proxy_ip)
                            self.proxy_ip = self.proxy_pool.get()
                    content = res.content.decode()
                    bs_content = BeautifulSoup(content, "lxml")
                    div_tags = bs_content.find_all(name="div", attrs={"class": "ffixWid00"})

                    # 数据库连接
                    orcl_conn = OracleSave()

                    for div_tag in div_tags:
                        code = div_tag.find(name="p", attrs={"class": "text14pt2 bold"}).text.strip()
                        chip1stop_code = div_tag.find(name="p", attrs={"class": "text10"}).text.strip()
                        print(chip1stop_code)
                        maker = div_tag.find(name="p", attrs={"class": "text10 wordBreak"}).text.strip()
                        component = (code, maker, category_name, category_url)

                        orcl_conn.component_insert(component)
                    orcl_conn.commit()
                    orcl_conn.conn.close()
            # ---------------------我是分割线-------------------

            # threading_pool = ThreadingPool()
            # threading_pool.multi_thread(thread_go, range(1, pages_count + 1))



if __name__ == "__main__":
    category = Category()
    category.get_product_list()
