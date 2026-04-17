import pdfplumber
import docx


def extract_text_from_file(file_path: str) -> str:
    text = ""

    try:
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])

    except Exception as e:
        print(f"Error extracting text from file: {e}")

    return text.strip()