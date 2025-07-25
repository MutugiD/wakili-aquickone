from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ConversationEntityMemory
from typing import Optional

class AgentMemory:
    """
    Unified interface for LangChain memory types: buffer, summary, entity.
    """
    def __init__(self, memory_type: str = "buffer", llm=None, k: int = 10, max_token_limit: int = 1000):
        self.memory_type = memory_type
        self.llm = llm
        if memory_type == "buffer":
            self.memory = ConversationBufferMemory(return_messages=True)
        elif memory_type == "summary":
            if llm is None:
                raise ValueError("LLM required for summary memory")
            self.memory = ConversationSummaryMemory(llm=llm, max_token_limit=max_token_limit, return_messages=True)
        elif memory_type == "entity":
            if llm is None:
                raise ValueError("LLM required for entity memory")
            self.memory = ConversationEntityMemory(llm=llm, k=k, return_messages=True)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def add_message(self, input_text: str, output_text: str = None):
        """
        Add a message to memory with proper input/output format for LangChain.
        """
        if output_text is None:
            output_text = ""
        self.memory.save_context({"input": input_text}, {"output": output_text})

    def get_history(self):
        return self.memory.load_memory_variables({})

    def clear(self):
        self.memory.clear()