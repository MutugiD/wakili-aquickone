# Extraction prompt templates for document extraction agent

structured_extraction_prompt = """
You are a legal assistant. Extract the following information from the provided legal document text:
- Parties involved (names of all parties)
- Effective date (if present)
- Termination date (if present)
- All clauses (summarize each clause or section)

If a field is not present, return null for that field.
Return the result as a JSON object with keys: parties, effective_date, termination_date, clauses.

Text:
{chunk}
"""