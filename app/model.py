import numpy as np
import torch
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
)
from sentence_transformers import SentenceTransformer


class LocalModel:
    def __init__(self, generation_model_name: str, embedding_model_name: str):
        self.generation_model_name = generation_model_name
        self.embedding_model_name = embedding_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.generation_model_name)
        config = AutoConfig.from_pretrained(self.generation_model_name)
        if config.is_encoder_decoder:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.generation_model_name)
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.generation_model_name)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.embedder = SentenceTransformer(self.embedding_model_name)

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        input_ids = inputs.input_ids.to(self.device)
        generation_kwargs = {
            "input_ids": input_ids,
            "max_length": max_tokens,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.95,
            "num_return_sequences": 1,
            "pad_token_id": self.tokenizer.eos_token_id or self.tokenizer.pad_token_id,
        }
        if "attention_mask" in inputs:
            generation_kwargs["attention_mask"] = inputs.attention_mask.to(self.device)

        outputs = self.model.generate(**generation_kwargs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    def embed(self, texts: list[str]) -> np.ndarray:
        embeddings = self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)
