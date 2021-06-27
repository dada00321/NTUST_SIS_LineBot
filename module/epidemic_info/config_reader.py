import configparser
from os.path import exists, abspath

def get_config():
    conf = configparser.ConfigParser()
    
    ''' Line Bot '''
    cfg_path = r"module/epidemic_info/ntu_system_config/ntu_system_config.ini"
	
    ''' exe ''' 
    #cfg_path = r"../ntu_system_config/ntu_system_config.ini"
    
    ''' test ''' 
    #cfg_path = r"./ntu_system_config/ntu_system_config.ini"

    #conf.read(cfg_path, encoding="utf-8")
    if exists(cfg_path):
        try:
            conf.read(cfg_path, encoding="utf-8")
            items = conf.items(conf.sections()[0])
            NTU_SYSTEM_SCHOOLS_NUM = 3
            epidemic_news_links = [items[i][1][1:-1] 
                                   for i in range(0, NTU_SYSTEM_SCHOOLS_NUM)]
            #print(epidemic_news_links)
            return epidemic_news_links
            
        except Exception as e:
            print(f"[WARNING] 發生未知錯誤\n錯誤訊息:\n{e}\n")
            return None
    else:
        print("[WARNING] 找不到組態(設定)檔案:\n"+\
              f"{abspath(cfg_path)}\n" +\
              "請確認此檔案或其上層目錄是否被刪除\n")

'''
if __name__ == "__main__":
    get_config()
'''