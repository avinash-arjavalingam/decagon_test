import json
from openai import OpenAI
from enum import Enum

class OutputTypes(Enum):
  FEATURE = 0
  BUG = 1

  def __str__(self):
    return self.name.lower().capitalize()

def query_conversation(prompt: str, open_ai_key: str):
  client = OpenAI(
    api_key=open_ai_key,
  )
  messages = [{"role": "user", "content": prompt}]
  temperature = 0
  answer = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=messages,
    temperature=temperature,
  )
  response = answer.choices[0].message.content
  return json.loads(response)
