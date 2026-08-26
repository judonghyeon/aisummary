from pyngrok import ngrok, conf
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NGROK_TOKEN")
if token:
    ngrok.set_auth_token(token)

public_url = ngrok.connect(8000)
print(f"\n외부 접속 URL: {public_url}\n")

# 터널 유지
input("엔터 누르면 종료...")
ngrok.disconnect(public_url)
