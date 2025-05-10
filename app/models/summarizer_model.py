from pydantic import BaseModel
from typing import Optional

class SummarizerModel(BaseModel):
    text: Optional[str] = None
    file: Optional[str] = None
    