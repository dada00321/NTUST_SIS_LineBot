"""
ntu_system_epidemic_info_assistant
臺灣大學系統-三校防疫資訊小助手
"""

from selenium import webdriver

#from config_reader import get_config
#from modules.basic_scraping_module import get_response

from module.epidemic_info.config_reader import get_config
from module.epidemic_info.modules.basic_scraping_module import get_response

from os.path import exists
from os import mkdir, listdir
from datetime import datetime
import re

class Epidemic_info_crawler():
    def crawl_epidemic_news(self, epidemic_news_links, school_abbrs, school_abbr):
        # 可由外部呼叫
        self.is_avaiable = False
        self.epidemic_news_link = None
        if school_abbr in school_abbrs:
            self.school_abbr = school_abbr
            tmp = epidemic_news_links[school_abbr]
            if tmp is not None and tmp.strip() != "":
                self.epidemic_news_link = tmp
                self.is_avaiable = True
            else:
                print("epidemic_news_links 連結無效")
            #--------------------
            content = self.selenium_crawl_epidemic_news()
            #content = self.requests_crawl_epidemic_news()
            if content is None:
                print("[WARNING] Epidemic_info_crawler 未抓取到任何內容")
            else:
                print("[INFO] 已抓取【防疫快訊】相關內容")
            return content
        else:
            print("[WARNING] Epidemic_info_crawler 輸入資訊錯誤\n"
                  "crawl_epidemic_news() 參數 `school_abbr` 不在 參數 `school_abbrs` 之中")
            return None
    # --------------------
    def selenium_crawl_epidemic_news(self):
        # 抓取臺灣大學系統(三校)防疫快訊 | i.e., 各校網站較重要的即時防疫訊息 | ※非防疫專區的各式訊息
        # 為求開發時間短、xpath 較通用的效益，先寫 selenium 而非 requests 或其它套件進行爬蟲的版本
        if self.is_avaiable:
            driver = self.get_web_driver(self.epidemic_news_link)
            content = None
            if self.school_abbr == "NTU":
                content = self.selenium_crawl_epidemic_news_NTU(driver)
            elif self.school_abbr == "NTNU":
                content = self.selenium_crawl_epidemic_news_NTNU(driver)
            elif self.school_abbr == "NTUST":
                content = self.selenium_crawl_epidemic_news_NTUST(driver)
            driver.quit()
            return content

    def get_web_driver(self, url):
        driver = webdriver.Chrome("D:/geckodriver/chromedriver.exe")
        driver.implicitly_wait(10)
        driver.get(url)
        return driver
    
    def selenium_crawl_epidemic_news_NTU(self, driver):
        content = dict()
        
        # 奇數列:
        odd_xpath = "//tr[@style='background-color:#EFF3FB;']"
        # 偶數列:
        even_xpath = "//tr[@style='background-color:White;']"
        
        # 1) 抓取所有 [日期] 欄位的 content
        # //tr[@style='background-color:#EFF3FB;']//td[contains(text(),'2021')]
        
        xpaths = [f"{date_xpath}//td[contains(text(),'{datetime.now().year}')]"
                  for date_xpath in (odd_xpath, even_xpath)]
        '''
        date_list = [tag.text.strip()
                     for xpath in xpaths
                     for tag in driver.find_elements_by_xpath(xpath)]
        '''

        tmp_list = [[],[]]
        count = 1
        for xpath in xpaths:
            for tag in driver.find_elements_by_xpath(xpath):
                tmp = tag.text.strip()
                if count % 2 == 1: 
                    count += 1
                    tmp_list[0].append(tmp)
                else:
                    tmp_list[1].append(tmp)
        
        date_list = list()
        len_odd, len_even = len(tmp_list[0]), len(tmp_list[1])
        for i in range(max(len_odd, len_even)):
            if i < len_odd: 
                date_list.append(tmp_list[0][i])
            if i < len_even: 
                date_list.append(tmp_list[1][i])
        print(date_list)
        content.setdefault("日期", date_list)
        
        # 2) 抓取所有 [標題] 欄位的 content
        #articleLink_xpath = "//td[contains(text(),'2021/5/20')]/../td[1]"
        #header_xpath = "//td[contains(text(),'2021/5/20')]/../td[2]"
        
        header_list = list()
        articleLink_list = list()
        header_xpath_pattern = "//td[contains(text(),'{}')]/../td[2]"
        articleLink_xpath_pattern = "//td[contains(text(),'{}')]/../td[1]"
        
        test = date_list[:1]
        for excution_count0, date in enumerate(test):
            header_xpath = header_xpath_pattern.format(date)
            articleLink_xpath = articleLink_xpath_pattern.format(date)
            
            # (2)
            tmp_header = driver.find_element_by_xpath(header_xpath).text
            if tmp_header is not None and str(tmp_header).strip()!='':
                # (deprecated) 原始 [標題] 同時有中英文 (較另二校內容較不易同步)
                #header_list.append(tmp_header)
                
                # [標題] 只保留中文部分
                if re.compile(r'[a-zA-Z]').search(tmp_header) is not None:
                    header_list.append(tmp_header[:tmp_header.index(re.compile(r'[a-zA-Z]').search(tmp_header).group())].strip())
                else:
                    header_list.append(tmp_header)
            
            # (3)
            '''tag_articleLink = driver.find_element_by_xpath(articleLink_xpath)
            tag_articleLink.click()'''
            driver.find_element_by_xpath(articleLink_xpath).click()
            
            print(f"[INFO] 正在抓取第 {1 + excution_count0} 篇防疫快訊")
            #tag.click()
            col_1_xpaths = "//td[@class='auto-style2']"
            col_2_xpaths = "//td[@class='auto-style1']"
            col1 = [tag.text.strip() 
                    for tag in driver.find_elements_by_xpath(col_1_xpaths)]
            col2 = [tag.text.strip() 
                    for tag in driver.find_elements_by_xpath(col_2_xpaths)]
            content_msg = '\n'.join([f"{k}: {v}" 
                                     for k, v in zip(col1, col2)
                                     if v is not None and v.strip()!=''])
            articleLink_list.append(content_msg)
            # 回上一頁
            driver.find_element_by_xpath("//input[@type='submit']").click()
        
        print("header_list:", header_list)
        print("articleLink_list:", articleLink_list)
        
        # 3) 抓取所有 [文章連結] 欄位的 content
        #articleLink_xpath_pattern = "//td[contains(text(),'{}')]/../td[1]"
        
        """
        # 2) 抓取所有 [標題] 欄位的 content
        #//tr[@style='background-color:#EFF3FB;']//td[contains(text(),'2021')]/../td[2]
        xpaths = [f"{date_xpath}//td[contains(text(),'{datetime.now().year}')]/../td[2]"
                  for date_xpath in (odd_xpath, even_xpath)]
        header_list = [tag.text
                       for xpath in xpaths
                       for tag in driver.find_elements_by_xpath(xpath)]
        """
        '''
        header_list = [s[:s.index(re.compile(r'[a-zA-Z]').search(s).group())].strip() 
                       if re.compile(r'[a-zA-Z]').search(s) is not None 
                       else s
                       for s in header_list]
        '''
        #print(header_list)
        
        # 3) 抓取所有 [文章連結] 欄位的 content
        """xpaths = [f"{date_xpath}//td[contains(text(),'{datetime.now().year}')]/../td[1]/a"
                  for date_xpath in date_xpaths]
        
        
        xpaths = [f"{date_xpath}//td[contains(text(),'{datetime.now().year}')]/../td[1]/a"
                  for date_xpath in (odd_xpath, even_xpath)]
        excution_times = 0
        articleLink_tags = [tag 
                            for xpath in xpaths
                            for tag in driver.find_elements_by_xpath(xpath)]
        """
        
        """
        while True:
        #for tag in articleLink_tags:
            excution_limit = len(articleLink_tags)
            if excution_times == excution_limit: 
                print(f"[INFO] 防疫快訊抓取完畢！共執行 {excution_limit} 次")
                break
            else:
                articleLink_tags[excution_times].click()
                excution_times += 1
                print(f"[INFO] 正在抓取第 {excution_times} 篇防疫快訊")
                #tag.click()
                col_1_xpaths = "//td[@class='auto-style2']"
                col_2_xpaths = "//td[@class='auto-style1']"
                col1 = [tag.text.strip() 
                        for tag in driver.find_elements_by_xpath(col_1_xpaths)]
                col2 = [tag.text.strip() 
                        for tag in driver.find_elements_by_xpath(col_2_xpaths)]
                content_msg = '\n'.join([f"{k}: {v}" 
                                         for k, v in zip(col1, col2)
                                         if v is not None and v.strip()!=''])
                print(content_msg)
                print("okk")
                tag = driver.find_element_by_xpath("//input[@type='submit']")
                tag.click() # 回上一頁
        """
        
        '''
        if len(articleLink_list) == 0: 
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " 無法抓取 [防疫快訊-文章連結] 故不往下執行")
            return None
        
        if len(date_list) == len(date_list) == len(date_list):
            content = {"日期": date_list,
                       "標題": header_list,
                       "文章連結": articleLink_list}
            return content

        else:
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " [防疫快訊] 底下資訊皆可抓取，但數量不相符，故不回傳資訊")
            return None
        '''
        return {"test":"1234"}
    
    def selenium_crawl_epidemic_news_NTNU(self, driver):
        content = dict()
        # 1) 抓取所有 [日期] 欄位的 content
        # 2) 抓取所有 [標題] 欄位的 content
        # 3) 抓取所有 [資訊連結] 欄位的 content # 資訊連結 | 原: 圖片連結
        # 4) 下載、儲存 所有 [圖片] content
        
        # //a[@class='thumbnail']
        xpath = "//a[@class='thumbnail']"
        tags = driver.find_elements_by_xpath(xpath)
        
        date_list = list()
        header_list = list()
        imagePath_list = list()
        
        for tag in tags[:3]:
            tmp = tag.get_attribute("data-title").split(' ')
            date_list.append(tmp[0])
            header_list.append(tmp[-1])
            src = tag.get_attribute("data-image")
            image_link = self.epidemic_news_link[:8] + self.epidemic_news_link[8:].split('/')[0] + src
            
            imagePath_list.append(image_link)
            """
            r = get_response(image_link)
            if r is not None:
                # Line Bot
                base_image_dir = "module/epidemic_info/media/"
                # exe:
                # ...
                # test:
                #base_image_dir = "./media/"
                if not exists(base_image_dir):
                    mkdir(base_image_dir)
                current_image_ID = len(listdir(base_image_dir)) + 1
                current_image_extension = ".jpg"
                current_image_fullpath = f"{base_image_dir}{current_image_ID}{current_image_extension}"
                imagePath_list.append(current_image_fullpath)
                try:
                    with open(current_image_fullpath, "wb") as fp:
                        fp.write(r.content)
                except:
                    print("[WARNING] 無法下載、儲存 [圖片] content")
            else:
                print("[WARNING] selenium_crawl_epidemic_news_NTNU()"+\
                      "無法抓取 [防疫快訊] 內容")
            """
        if len(date_list) == len(date_list) == len(date_list):
            '''
            content = {"日期": date_list,
                       "標題": header_list,
                       "圖片路徑": imagePath_list}
            '''
            content = {"日期": date_list,
                       "標題": header_list,
                       "資訊連結": imagePath_list} # 資訊連結 | 原: 圖片連結
            return content
        else:
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " [防疫快訊] 底下資訊皆可抓取，但數量不相符，故不回傳資訊")
            return None
    
    def selenium_crawl_epidemic_news_NTUST(self, driver):
        content = dict()
        
        # //h2[contains(text(),'本校最新訊息')]
        # //h2[contains(text(),'本校最新訊息')]/../../section
        # //h2[contains(text(),'本校最新訊息')]/../../section/table
        ''' 抓取 [有關防疫快訊的 table] 裡面的 [日期], [標題], [文章連結] '''
        # 1) 抓取所有 [日期] 欄位的 content
        # //h2[contains(text(),'本校最新訊息')]/../../section/table//td[@data-th='日期']/div
        xpath = "//h2[contains(text(),'本校最新訊息')]/../../section/table//td[@data-th='日期']/div"
        date_list = [tag.text.strip()
                     for tag in driver.find_elements_by_xpath(xpath)]
        #print(*(e for e in date_list))
        if len(date_list) == 0: 
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " 無法抓取 [防疫快訊-日期] 故不往下執行")
            return None

        # 2) 抓取所有 [標題] 欄位的 content
        # //h2[contains(text(),'本校最新訊息')]/../../section/table//td[@data-th='標題']//a
        #import time 
        #time.sleep(5)
        xpath = "//h2[contains(text(),'本校最新訊息')]/../../section/table//td[@data-th='標題']//a"
        headers = driver.find_elements_by_xpath(xpath)
        header_list = [tag.text.strip()
                       for tag in headers]
        #print(header_list)
        if len(header_list) == 0: 
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " 無法抓取 [防疫快訊-標題] 故不往下執行")
            return None

        # 3) 抓取所有 [文章連結] 欄位的 content
        # ※ 沿用 headers ([文章連結] 與 [標題] 的 content 為同一網頁元素)
        articleLink_list = [tag.get_attribute("href")
                            for tag in headers]
        #print(articleLink_list)
        if len(articleLink_list) == 0: 
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " 無法抓取 [防疫快訊-文章連結] 故不往下執行")
            return None
        
        if len(date_list) == len(date_list) == len(date_list):
            content = {"日期": date_list,
                       "標題": header_list,
                       "文章連結": articleLink_list}
            return content

        else:
            print("[WARNING] selenium_crawl_epidemic_news_NTUST()"+\
                  " [防疫快訊] 底下資訊皆可抓取，但數量不相符，故不回傳資訊")
            return None
    # --------------------
    def requests_crawl_epidemic_news(self):
        # 以後有空再寫，先 pass
        pass

class Epidemic_info_assistant():
    def __init__(self):
        self.epidemic_news_links = None
        # --------------------
        self.school_abbrs = ("NTU", "NTNU", "NTUST")
        self.read_config()
    
    def read_config(self):
        tmp_info = get_config()
        if tmp_info is not None:
            #NTU_SYSTEM_SCHOOLS_NUM = 3
            #print(*(f"{tmp_info[i]}" for i in range(0, NTU_SYSTEM_SCHOOLS_NUM)), sep='\n'*2)
            epidemic_news_links = {self.school_abbrs[0]: tmp_info[0],
                                   self.school_abbrs[1]: tmp_info[1],
                                   self.school_abbrs[2]: tmp_info[2]}
            #print(epidemic_news_links["NTUST"])
            self.epidemic_news_links = epidemic_news_links
    
    def crawl_ntu_system_news(self, input_text):
        # 利用 Epidemic_info_crawler 抓取臺灣大學系統(三校)防疫快訊
        crawler = Epidemic_info_crawler()
        
        # 取得爬蟲內容
        content = crawler.crawl_epidemic_news(self.epidemic_news_links, self.school_abbrs, input_text)
        
        if input_text in ('NTU', 'NTUST'):
            fields = ["日期", "標題", "文章連結"]
            #print(*(f'content["{field}"]: {content[field]}' for field in fields), sep='\n'*2)
            #print(*(f"|{k} --- {v}|" for k, v in content.items()), sep='\n')
        
        elif input_text == 'NTNU':
            #fields = ["日期", "標題", "圖片路徑"] # (暫緩)
            fields = ["日期", "標題", "資訊連結"] # 資訊連結 | 原: 圖片連結

        msg = ""
        article_num = len(content[fields[0]])
        for i in range(article_num):
            for field in fields:
                msg += f"{field}： {content[field][i]}\n"
            msg += '\n'
        return msg

'''    
if __name__ == "__main__":
    #input_text = "NTU" # 使用者輸入資訊
    #input_text = "NTNU" # 使用者輸入資訊
    input_text = "NTUST" # 使用者輸入資訊
    
    assistant = Epidemic_info_assistant()
    content = assistant.crawl_ntu_system_news(input_text) # 抓取防疫快訊
    print(content)
    print(type(content))
'''