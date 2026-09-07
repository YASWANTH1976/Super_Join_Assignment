import sqlite3

def fallback_comparison():
    conn = sqlite3.connect('knowledge_layer.db')
    c = conn.cursor()
    
    c.execute("SELECT id, entity, metric, value, timeframe, source_quote FROM facts")
    all_facts = c.fetchall()
    
    # Group by Entity and Metric to find overlaps
    grouped = {}
    for f in all_facts:
        key = f"{f[1]}_{f[2]}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(f)
        
    print(f"Fallback Engine: Processing {len(grouped)} metric groups...\n")
    
    for key, facts in grouped.items():
        if len(facts) < 2:
            continue # Need at least 2 to compare
            
        f1, f2 = facts[0], facts[1]
        v1, v2 = str(f1[3]).strip().lower(), str(f2[3]).strip().lower()
        t1, t2 = str(f1[4]).strip().lower(), str(f2[4]).strip().lower()
        
        # Local Logic Engine
        if v1 == v2:
            rel_type = "Corroboration"
            explanation = "Values match exactly across document extractions."
        elif t1 != t2:
            rel_type = "Explained Contradiction"
            explanation = f"Values differ because timeframes differ ({f1[4]} vs {f2[4]})."
        else:
            rel_type = "Hard Contradiction"
            explanation = "Values conflict within the same timeframe context."
            
        c.execute('''INSERT INTO relationships (fact1_id, fact2_id, relationship_type, explanation) 
                     VALUES (?, ?, ?, ?)''', (f1[0], f2[0], rel_type, explanation))
        
        print(f"Logged {rel_type} for {key}")
    
    conn.commit()
    conn.close()
    print("\nDatabase updated via Local Fallback Engine.")

if __name__ == "__main__":
    fallback_comparison()