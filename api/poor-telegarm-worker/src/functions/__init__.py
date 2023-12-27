from src.custom_client import CustomClient
from src.sessions_hub import SessionTask
from src.functions.account import Account
from src.functions.contacts import Contacts
from src.functions.messages import Messages


class Function(Account, Contacts, Messages):
    def __init__(self, task: SessionTask, client: CustomClient):
        self.task = task
        self.client = client
