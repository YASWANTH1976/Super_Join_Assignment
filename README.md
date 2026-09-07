# Superjoin Assignment: Fact Knowledge Layer

**Watch the Demo Video:** [Click here to watch the Loom Demo](https://www.loom.com/share/58a751d6cbd64b268709c869e139a252)

## 🏗️ System Architecture
This Fact Knowledge Layer was built to extract, compare, and ground facts from financial PDFs (like the Delhivery Prospectus) with strict deterministic provenance.

* **Tech Stack:** Python, PyMuPDF, Google Gemini API, SQLite, FastAPI.
* **Relational over Vector:** I deliberately chose a standard relational SQLite database (`knowledge_layer.db`) instead of a Vector DB. This ensures every extracted fact is strictly tied to a specific Document ID, Page Number, and exact Source Quote, preventing LLM hallucinations.

## 🚀 Key Features
1. **Strict JSON Schema Enforcement:** PDF text is streamed to Gemini to enforce structured extractions.
2. **Graceful Failure & Offline Fallback:** If the system hits Google API rate limits (e.g., HTTP 429/503) during bulk extraction, the app does not crash. It catches the error, saves successful pages, and shifts the comparison logic to an offline local engine (`local_compare.py`).
3. **Relationship Dashboard:** A FastAPI dashboard visualizes three relationship types:
   * **Corroboration:** Facts perfectly match across extractions.
   * **Explained Contradiction:** Values differ but are resolved via temporal context (e.g., 9-month period vs. full financial year).
   * **Hard Contradiction:** Conflicting values within the exact same timeframe are flagged red for human review.

## 💻 How to Run the Project

**1. Run the Primary Extraction (API):**
`python compare_facts.py`

**2. Run the Offline Fallback Engine (If API fails):**
`python local_compare.py`

**3. Launch the Dashboard:**
`python -m uvicorn main:app --reload`

*Then open http://127.0.0.1:8000 in your web browser.*
