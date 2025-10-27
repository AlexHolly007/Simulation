from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# List all models available to your verified organization
models = client.models.list()

# Print only the model IDs for readability
for m in models.data:
    print(m.id)