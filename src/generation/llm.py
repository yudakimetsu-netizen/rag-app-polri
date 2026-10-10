from langchain_openai import ChatOpenAI
from src.config import NEOSANTARA_API_KEY, BASE_URL, LLM_MODEL

_llm = None


def get_llm():
    """Get cached LLM instance."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=NEOSANTARA_API_KEY,
            base_url=BASE_URL,
            temperature=0,
        )
    return _llm