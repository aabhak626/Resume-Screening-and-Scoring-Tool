import PyPDF2

def get_resume_text(file_path):
    text = ""

    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            print(f"Pages: {len(reader.pages)}")

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                print(f"Page {i} text: {page_text}")

                if page_text:
                    text += page_text

    except Exception as e:
        print("Extraction error:", e)

    return text