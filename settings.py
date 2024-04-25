import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
