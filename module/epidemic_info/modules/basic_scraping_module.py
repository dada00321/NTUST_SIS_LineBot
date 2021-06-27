import requests
from bs4 import BeautifulSoup as bs
#from fake_useragent import UserAgent

def get_response(url):
	#headers = {"User-Agent": UserAgent().random}
	#r = requests.get(url, headers=headers)
	r = requests.get(url)
	
	if r.status_code == requests.codes.ok: 
		print("[INFO] 正在抓取圖片")
		r.encoding = "utf-8"
		return r
	
	else:
		print("[WARNING] 抓取圖片失敗，無法取得連線")
		return None
	
def get_soup(response):
	return bs(response.text, "lxml")