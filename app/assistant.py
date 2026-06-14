from .config import settings
from .memory import MemoryStore
from .model import LocalModel


class JarvisAssistant:
    def __init__(self):
        self.settings = settings
        self.memory = MemoryStore(self.settings.memory_db)
        self.model = LocalModel(self.settings.model_name, self.settings.embedding_model)

    def _build_prompt(self, user_message: str, relevant_memory: list[dict[str, str]]) -> str:
        memory_section = "\n".join(
            [f"{item['role'].capitalize()}: {item['content']}" for item in relevant_memory]
        )
        if memory_section:
            memory_section = f"Relevant context:\n{memory_section}\n\n"

        prompt = (
            f"You are {self.settings.assistant_name}, a helpful local assistant. "
            "Keep responses brief, helpful, and friendly.\n\n"
            f"{memory_section}"
            "Conversation:\n"
            f"User: {user_message}\n"
            f"Assistant:"
        )
        return prompt

    def reply(self, user_message: str) -> str:
        query_embedding = self.model.embed([user_message])[0]
        relevant_memory = self.memory.retrieve_relevant(query_embedding, limit=self.settings.top_memory)

        prompt = self._build_prompt(user_message, relevant_memory)
        response = self.model.generate(prompt, max_tokens=256)

        self.memory.add_interaction("user", user_message, embedding=query_embedding)
        response_embedding = self.model.embed([response])[0]
        self.memory.add_interaction("assistant", response, embedding=response_embedding)
        self.memory.prune(self.settings.max_memory_items)

        return response
