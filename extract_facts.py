import pymupdf as fitz
import sqlite3
import json
import os
import time
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

def clean_json(text):
    text = text.strip()
    if text.startswith("```json"): text = text[7:]
    elif text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    return text.strip()

def process_pdf(pdf_path):
    conn = sqlite3.connect('knowledge_layer.db')
    c = conn.cursor()
    
    filename = os.path.basename(pdf_path)
    c.execute("INSERT INTO documents (filename) VALUES (?)", (filename,))
    doc_id = c.lastrowid
    
    doc = fitz.open(pdf_path)
    print(f"\nProcessing {filename} ({len(doc)} pages)...")
    
    # Tip: Change range(len(doc)) to range(5) if you want a fast 5-page test
    # Change this:
    # for page_num in range(len(doc)):

    # To this (scans the first 20 pages):
    for page_num in range(min(20, len(doc))):
        text = doc[page_num].get_text("text")
        if not text.strip():
            continue
            
        print(f"  -> Scanning page {page_num + 1}...")
        
        prompt = f"""
        Extract key numerical, financial, and organizational facts from the following text.
        Return ONLY a valid JSON list of objects with these exact keys:
        "entity": (e.g., "Delhivery", "Subsidiary XYZ")
        "metric": (e.g., "Revenue", "Active Directors", "Warehouse Area")
        "value": (The actual number or status)
        "timeframe": (e.g., "FY24", "Q3 2022", "As of May 2022", or "N/A")
        "source_quote": (The exact short sentence proving this fact)
        
        If no major facts exist, return an empty list [].
        
        Text:
        {text}
        """
        
        try:
            response = client.models.generate_content(
            model='gemini-3.6-flash', # <-- Update this line
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
)
            
            
            facts = json.loads(clean_json(response.text))
            
            for fact in facts:
                c.execute('''INSERT INTO facts 
                             (doc_id, entity, metric, value, timeframe, source_quote, page_num)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (doc_id, fact.get('entity'), fact.get('metric'), str(fact.get('value')), 
                           fact.get('timeframe'), fact.get('source_quote'), page_num + 1))
            conn.commit()
            
        except Exception as e:
            # Print the exact error instead of hiding it
            print(f"    [!] Error on page {page_num + 1}: {e}")
            
        # Crucial: 4-second delay keeps us at 15 RPM to avoid API bans
        time.sleep(4)
            
    conn.close()
    print(f"Finished processing {filename}.\n")

if __name__ == "__main__":
    target_pdf = "01-delhivery-prospectus-2022-excerpt.pdf"
    if os.path.exists(target_pdf):
        process_pdf(target_pdf)
    else:
        print(f"Error: {target_pdf} not found.")