import sqlite3

def init_db():
    conn = sqlite3.connect('knowledge_layer.db')
    c = conn.cursor()
    
    # Table 1: Source Documents
    c.execute('''CREATE TABLE IF NOT EXISTS documents 
                 (id INTEGER PRIMARY KEY, filename TEXT, upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table 2: Extracted Facts
    c.execute('''CREATE TABLE IF NOT EXISTS facts 
                 (id INTEGER PRIMARY KEY, doc_id INTEGER, entity TEXT, metric TEXT, 
                  value TEXT, timeframe TEXT, source_quote TEXT, page_num INTEGER)''')
    
    # Table 3: Relationships (The core of the assignment: Corroborations & Contradictions)
    c.execute('''CREATE TABLE IF NOT EXISTS relationships 
                 (id INTEGER PRIMARY KEY, fact1_id INTEGER, fact2_id INTEGER, 
                  relationship_type TEXT, explanation TEXT)''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("SQLite Database initialized successfully.")