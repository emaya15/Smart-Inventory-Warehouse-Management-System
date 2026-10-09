import datetime
import random
import string
from sqlalchemy.orm import Session

def generate_document_number(prefix: str, db: Session, model, number_column: str) -> str:
    today_str = datetime.date.today().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    doc_number = f"{prefix}-{today_str}-{random_suffix}"
    return doc_number
