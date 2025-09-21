from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class PushNotification(BaseModel):
    """Mensagem a ser enviada ao usuário"""
    message: str = Field(..., description="Mensagem a ser enviada ao usuário.")

class PushNotificationTool(BaseTool):
    

    name: str = "Enviar uma notificação push"
    description: str = (
        "Esta ferramenta é usada para enviar uma notificação push ao usuário."
    )
    args_schema: Type[BaseModel] = PushNotification

    def _run(self, message: str) -> str:
        pushover_user = os.getenv("PUSHOVER_USER")
        pushover_token = os.getenv("PUSHOVER_TOKEN")
        pushover_url = "https://api.pushover.net/1/messages.json"

        print(f"Notificação: {message}")
        payload = {"user": pushover_user, "token": pushover_token, "message": message}
        requests.post(pushover_url, data=payload)
        return '{"notificacao": "ok"}'

