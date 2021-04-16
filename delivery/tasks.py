import requests
from celery import shared_task
from backend_test.settings import SLACK_TOKEN, TEMPLATE_NOTIFICATION

# Tarea de envío de notificación a compradores
@shared_task()
def send_notification_shopper(shoppers):
	# Se recorren todos los compradores
	for shopper in shoppers:
		data = {
				'token': SLACK_TOKEN, # Token de apliación en Slack
				'channel': shopper.idSlack, # ID del comprador en Slack. 
				'as_user': True,
				'text': TEMPLATE_NOTIFICATION + str(shopper.id) #Plantilla personalizada 
				}
		# Se envía el request a Slack para publicar el mensaje
		requests.post(url='https://slack.com/api/chat.postMessage',data=data)
	return None
 



