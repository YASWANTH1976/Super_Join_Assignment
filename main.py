from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    conn = sqlite3.connect('knowledge_layer.db')
    c = conn.cursor()
    
    # Fetch relationships and their source facts
    c.execute('''
        SELECT r.relationship_type, r.explanation, 
               f1.entity, f1.metric, f1.value, f1.source_quote, 
               f2.value, f2.source_quote
        FROM relationships r
        JOIN facts f1 ON r.fact1_id = f1.id
        JOIN facts f2 ON r.fact2_id = f2.id
    ''')
    rels = c.fetchall()
    conn.close()
    
    # Raw, hacker-style HTML UI
    html = "<body style='font-family: monospace; background: #1e1e1e; color: #00ff00; padding: 20px;'>"
    html += "<h2>[ Superjoin Fact Knowledge Layer - Dashboard ]</h2><hr>"
    html += f"<h3>System Status: <span style='color:orange'>API Rate Limited (429) -> Local Fallback Engaged</span></h3>"
    html += "<ul>"
    
    for r in rels:
        color = "#00ff00" if r[0] == "Corroboration" else "#ff4444" if r[0] == "Hard Contradiction" else "#ffff00"
        html += f"<li style='margin-bottom: 20px; border-left: 2px solid {color}; padding-left: 10px;'>"
        html += f"<strong style='color:{color}'>[{r[0].upper()}]</strong> {r[1]}<br>"
        html += f"<b>Entity/Metric:</b> {r[2]} - {r[3]}<br>"
        html += f"<i>Fact A:</i> {r[4]} <span style='color:#888'>(Source: '{r[5]}')</span><br>"
        html += f"<i>Fact B:</i> {r[6]} <span style='color:#888'>(Source: '{r[7]}')</span>"
        html += "</li>"
        
    html += "</ul></body>"
    return html