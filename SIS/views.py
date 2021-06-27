from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage

from module import func

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
	if request.method == 'POST':
		signature = request.META['HTTP_X_LINE_SIGNATURE']
		body = request.body.decode('utf-8')

		try:
		   events = parser.parse(body, signature)
		except InvalidSignatureError:
		   return HttpResponseForbidden()
		except LineBotApiError:
		   return HttpResponseBadRequest()
		   
		for event in events:
			if isinstance(event, MessageEvent):
				'''
				line_bot_api.reply_message(event.reply_token,
				   TextSendMessage(text=event.message.text))
				'''
				if isinstance(event.message, TextMessage):
					text = event.message.text
					if "二退" in text:
						func.cancel_course(event)
					
					elif text == "@我要提問":
						func.raise_new_question(event, "case_1")
					
					elif text == "@常見Q&A":
						func.command_q_and_a(event)

					elif text == "@疫情資訊":
						func.epidemic_info(event, "init")

					elif text == "@三校資訊":
						func.ntu_system(event)
					
					else:
						text = text.replace('.', '').strip()
						if text.isdigit():
							# @疫情資訊 使用者回覆的的代號
							if int(text) in range(1,4):
								func.epidemic_info(event, text)
							else:
								func.epidemic_info(event, "err")
						else:
							# @我要提問 使用者回覆的的問題
							func.raise_new_question(event, "case_2")
		return HttpResponse()
	else:
		return HttpResponseBadRequest()