import json
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

# Load PDF and extract text
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n".join(text)

# Function to strip header, footer, and footnotes
# this function does not properly work, and this stripping was done manually with vscode "find and replace"
def strip_header_footer(text):
    # Regex pattern to identify header variations: both 'DA\nEUT L, 12.7.2024' and 'EUT L, 12.7.2024\nDA'
    header_pattern = r"(DA\s*\n\s*EUT L, \d{1,2}\.\d{1,2}\.\d{4}|EUT L, \d{1,2}\.\d{1,2}\.\d{4}\s*\n\s*DA)"
    
    # Updated footer pattern to handle page numbers and multi-line footers
    footer_pattern = r"(\n(\d+/\d+)\s*ELI: http://data\.europa\.eu/eli/reg/\d{4}/\d{4}/oj|\nELI: http://data\.europa\.eu/eli/reg/\d{4}/\d{4}/oj\s*(\d+/\d+))"
    # The footer pattern is now able to match both "8/144 ELI: ..." and "ELI: ... 8/144"
    
    # Updated footnote pattern to capture footnotes and remove them (e.g., "(1) EUT C 517 ...")
    footnote_pattern = r"\(\d+\)[^\n]*|(?:\(\d+\)\s*.*?)(?=\n|\r|\z)"  # Matches footnotes like (1) EUT C 517... or footnotes across multiple lines
    
    # Remove header, footer, and footnotes by replacing them with an empty string
    text = re.sub(header_pattern, "", text)
    text = re.sub(footer_pattern, "", text)
    text = re.sub(footnote_pattern, "", text)
    
    # Clean up any additional empty lines or unwanted spaces that may appear
    text = re.sub(r"\n\s*\n", "\n", text)  # Remove extra empty lines
    
    return text

# Load the legal document
pdf_path = "euactNB.pdf"  # Update path as needed
document_text = extract_text_from_pdf(pdf_path)

# Strip header, footer, and footnotes from the document text
cleaned_text = strip_header_footer(document_text)

# Configure LangChain Text Splitter with sentence-based splitting
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Adjust chunk size as needed
    chunk_overlap=200,  # Overlapping ensures better context retention
    separators=["\n\n", "\n", " ", ""],  # Prioritize logical breaks
    length_function=len
)

# Generate chunks
chunks = splitter.split_text(cleaned_text)

# Post-processing step: Check if a chunk ends with an incomplete sentence
def fix_incomplete_chunks(chunks):
    fixed_chunks = []
    current_chunk = ""

    for chunk in chunks:
        # If the chunk ends with an incomplete sentence, merge it with the next chunk
        if chunk.endswith(('.', '!', '?')):  # End of sentence
            if current_chunk:
                fixed_chunks.append(current_chunk)
            current_chunk = chunk
        else:
            current_chunk += " " + chunk

    if current_chunk:
        fixed_chunks.append(current_chunk)

    return fixed_chunks

# Fix chunks by merging incomplete sentences
fixed_chunks = fix_incomplete_chunks(chunks)

# Structure chunks into JSON
json_chunks = [{"id": idx, "text": chunk} for idx, chunk in enumerate(fixed_chunks)]

# Save to JSON file with proper encoding (ensure_ascii=False)
output_file = "chunked_legal_document_fixed.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(json_chunks, f, ensure_ascii=False, indent=4)

print(f"Chunked document saved to {output_file}")
