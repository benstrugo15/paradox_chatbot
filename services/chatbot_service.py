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

        if context_messages:
            is_follow_up = self._is_follow_up_question(message, context_messages)
            if is_follow_up:
                messages.append({
                    "role": "system",
                    "content": "This is a follow-up question. Please maintain context from the previous conversation."
                })

            messages.extend(context_messages)

        messages.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"}
        )

        return json.loads(completion.choices[0].message.content)["answer"]

    def _is_follow_up_question(self, current_message: str, context_messages: List[Dict]) -> bool:
        if not context_messages:
            return False

        last_user_message = next(
            (msg["content"] for msg in reversed(context_messages) if msg["role"] == "user"),
            None
        )

        if not last_user_message:
            return False

        follow_up_indicators = ["and", "what about", "how about", "also", "in addition"]
        current_message_lower = current_message.lower()

        if any(current_message_lower.startswith(indicator) for indicator in follow_up_indicators):
            return True

        prompt = f"""Is the following message a follow-up question to the previous context?
Previous context: {last_user_message}
Current message: {current_message}
Answer with only 'yes' or 'no'."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )

        return response.choices[0].message.content.strip().lower() == "yes"

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

{formatted_data}

When answering follow-up questions, maintain context from previous messages.
If a question is unclear or lacks context, ask for clarification.

Provide an answer in the following JSON format:
{{
    "answer": string
}}
"""
