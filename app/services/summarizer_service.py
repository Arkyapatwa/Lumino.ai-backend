from utils.llm import LLM
from models.summarizer_model import SummarizerModel
from fastapi import Request

def summarize_text(user_input: SummarizerModel, request: Request):
    llm = LLM()
    model = llm.get_openai_model()

    prompt = f"""
        Summarize this text below.

        Text:{user_input.text}
    """

    response = model.invoke(prompt)
    result = {
        "result": response.content
    }
    return result

def summarize_file(user_input: SummarizerModel, request: Request):
    pass