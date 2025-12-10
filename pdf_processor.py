import io
from typing import List
import pypdf

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extracts raw text from a PDF file content.
    """
    try:
        pdf_file = io.BytesIO(file_content)
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        page_count = len(reader.pages)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text, page_count

    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")

def clean_text(text: str) -> str:
    """
    Cleans the extracted text by removing excessive whitespace and non-ASCII characters.
    """
    # Remove non-ASCII characters
    text = text.encode("ascii", "ignore").decode()
    # Replace multiple newlines with a single newline
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Splits the text into smaller chunks for embedding.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks

if __name__ == "__main__":
    # Test with a dummy file if needed
    pass
