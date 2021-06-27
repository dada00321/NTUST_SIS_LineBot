from django.conf import settings
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage,\
	StickerSendMessage, LocationSendMessage, QuickReply,\
	QuickReplyButton, MessageAction
from module.epidemic_info.ntu_system_epidemic_info_assistant import Epidemic_info_assistant

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

def cancel_course(event):
	msg = "二退的方式可以透過截圖二退單的方式傳給老師，老師審核後可以透過回email的答覆方式做為老師的簽名。\n"+\
		  "解答來源可以參考 以下連結:\n"+\
		  "https://demoadmin.ntust.edu.tw/p/404-1048-78756.php?Lang=zh-tw"
	message = TextSendMessage(text=msg)
	line_bot_api.reply_message(event.reply_token, message)

def raise_new_question(event, resp_case): # @我要提問
	try:
		if resp_case == "case_1":
			msg = "請輸入您的問題(左下角小鍵盤輸入)："
			message = TextSendMessage(text=msg)
			line_bot_api.reply_message(event.reply_token, message)
			
			print(event.message.text)

		elif resp_case == "case_2":
			msg = "台科緊急應變小助手已收到您的訊息~~ 謝謝您的來訊！"
			message = TextSendMessage(text=msg)
			line_bot_api.reply_message(event.reply_token, message)
	except:
		msg = "發生錯誤"
		message = TextSendMessage(text=msg)
		line_bot_api.reply_message(event.reply_token, message)

def command_q_and_a(event): # @常見Q&A
	pass
	
def epidemic_info(event, resp_msg): # @疫情資訊
	try:
		if resp_msg == "init":
			msg = "1.台大 2.台師大 3.台科大\n"+\
				  "請輸入代號 (1 / 2 / 3) 爬取相關的疫情資訊(左下角小鍵盤輸入)："
		
		elif resp_msg == "err":
			msg = "輸入資訊有誤！\n"+\
				  "1.台大 2.台師大 3.台科大\n"+\
				  "代號只能為以下任一者 (1 / 2 / 3)\n\n"+\
				  "請重新點選圖片選單：【疫情資訊】再輸入代號，謝謝您"
		
		else:
			msg = "正在啟動【疫情資訊】內容獲取服務\n"
			msg += f"任務代號:{resp_msg}\n\n"
			msg += "台科緊急應變小助手正加速運行中，請稍等~"
			
			if resp_msg == '1':
				input_text = "NTU"
			elif resp_msg == '2':
				input_text = "NTNU"
			elif resp_msg == '3':
				input_text = "NTUST"
			
			assistant = Epidemic_info_assistant()
			msg = assistant.crawl_ntu_system_news(input_text) # 抓取防疫快訊
	
	except:
		msg = "發生錯誤"
		
	finally:
		message = TextSendMessage(text=msg)
		line_bot_api.reply_message(event.reply_token, message)
	
def ntu_system(event): # @三校資訊
	pass
	