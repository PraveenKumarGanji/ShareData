You are an expert AI engineer building a Streamlit proof-of-concept for FinCEN Suspicious Activity Report (SAR) narrative generation.

🎯 Objective:
Create a working Streamlit web app called **"SAR Narrative Generator (PoC)"** that helps analysts generate FinCEN-style SAR narratives from structured case data.

📂 Project structure:
sar_streamlit_app/
 ├── app.py                 # Main Streamlit app
 ├── sample_sar.json        # Example SAR case data
 ├── requirements.txt       # Dependencies (streamlit only for now)
 └── README.md              # Basic documentation and usage

---

### Functional Requirements:

1. **Input methods (sidebar):**
   - Option to upload a JSON file (structured SAR case)
   - Option to load a sample SAR case
   - Option to manually input data via a simple Streamlit form

2. **Generate Narrative:**
   - Use a **template-based generator** (no LLM for PoC) that builds a narrative summarizing the case.
   - Template should include:
     - Customer name/type
     - Activity period
     - Transaction summary
     - Alert reason
     - Detection system
     - Analyst notes
     - “Reason for suspicion” section
     - “Recommendation” section

3. **Editing & Validation:**
   - Show generated narrative in a large editable text area.
   - Run simple compliance checks (e.g., look for “structuring”, “terrorism”, short narrative warnings).

4. **Export:**
   - Allow export of final narrative as:
     - `.txt` file
     - `.json` package (includes case data, narrative, timestamp)

5. **UI:**
   - Use Streamlit wide layout.
   - Include sidebar toggles and descriptive markdown headers.

---

### Example case data (sample_sar.json):
```json
{
  "case_id": "SAR-2025-0926",
  "customer_name": "John D. Smith",
  "customer_type": "Individual",
  "linked_entity": "JD Smith Consulting LLC",
  "activity_period": "2025-09-10 to 2025-09-25",
  "transaction_summary": [
    {"type": "Cash Deposit", "count": 48, "amount_range": "$9,000–$9,800", "total": "$450,000"},
    {"type": "Wire Transfer", "count": 1, "amount": "$440,000", "destination": "Global Trade Co. Ltd., Hong Kong"}
  ],
  "alert_reason": "Structuring activity below $10,000 threshold",
  "detection_system": "AML Transaction Monitoring v2.3",
  "analyst_notes": "Frequent cash deposits across branches; funds consolidated before international wire transfer."
}
