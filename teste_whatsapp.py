from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

message = client.messages.create(
    body="Teste de alerta do DashFin! ✅",
    from_=os.getenv("TWILIO_WHATSAPP_FROM"),
    to=os.getenv("ALERT_WHATSAPP_TO")
)

print("Mensagem enviada! SID:", message.sid)
