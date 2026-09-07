import sqlite3
import json
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

def analyze_relationships():
    conn = sqlite3.connect('knowledge_layer.db')
    c = conn.cursor()
    
    c.execute("SELECT id, entity, metric, value, timeframe, source_quote, doc_id FROM facts")
    all_facts = c.fetchall()
    
    # Group facts by entity and metric to find overlap
    grouped_facts = {}
    for f in all_facts:
        key = f"{f[1]}_{f[2]}" 
        if key not in grouped_facts:
            grouped_facts[key] = []
        grouped_facts[key].append(f)
        
    print(f"Found {len(grouped_facts)} unique metrics. Looking for overlap...")
    
    for key, facts in grouped_facts.items():
        if len(facts) < 2:
            continue # We need at least 2 facts to compare
            
        print(f"\nAnalyzing overlap for: {key}...")
        f1, f2 = facts[0], facts[1]
        
        prompt = f"""
        Compare these two extracted facts from financial documents. 
        Fact 1: Value: {f1[3]}, Timeframe: {f1[4]}, Source: "{f1[5]}"
        Fact 2: Value: {f2[3]}, Timeframe: {f2[4]}, Source: "{f2[5]}"
        
        Analyze their relationship. Return ONLY a valid JSON object with these keys:
        "relationship_type": (Must be exactly one of: "Corroboration", "Hard Contradiction", "Explained Contradiction")
        "explanation": (A 1-sentence explanation of why. e.g., 'Numbers differ because they represent different financial quarters.')
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = json.loads(clean_json(response.text))
            rel_type = result.get('relationship_type')
            
            c.execute('''INSERT INTO relationships 
                         (fact1_id, fact2_id, relationship_type, explanation) 
                         VALUES (?, ?, ?, ?)''',
                      (f1[0], f2[0], rel_type, result.get('explanation')))
            conn.commit()
            
            print(f"  -> {rel_type}: {result.get('explanation')}")
            time.sleep(4) 
            
        except Exception as e:
            print(f"  [!] Failed to analyze {key}: {e}")
            
    conn.close()
    print("\nRelationship engine complete. Database updated.")

if __name__ == "__main__":
    analyze_relationships()