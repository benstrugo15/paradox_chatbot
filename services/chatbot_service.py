import json
from typing import List, Dict, Optional
from openai import OpenAI
from config import OPENAI_KEY


class Chatbot:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_KEY)

    def search(self, data: List[Dict], message: str, context_messages: Optional[List[Dict]] = None) -> str:
        system_prompt = self._build_system_prompt(data)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context messages if available
        if context_messages:
            messages.extend(context_messages)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            response_format={"type": "json_object"}
        )

        return json.loads(completion.choices[0].message.content)["answer"]

    def _build_system_prompt(self, retrieved_data: List[Dict]) -> str:
        formatted_data = "\n-----\n".join(
            [
                f"Name: {startup['name']}\nCity: {startup['city']}\nDescription:{startup['description']}"
                for startup in retrieved_data
            ]
        )
        return f"""You are a Q&A chatbot that answers questions about start-ups.
Keep your answers short and to the point.
Your whole knowledge is the following information:

###
{formatted_data}
###

When answering follow-up questions, maintain context from previous messages.
If a question is unclear or lacks context, ask for clarification.

Provide an answer in the following JSON format:
{{
    "answer": string
}}
"""
