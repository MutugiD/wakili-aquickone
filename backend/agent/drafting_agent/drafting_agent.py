from typing import Dict, Any
from backend.utils.save_utils import save_drafted_document
from backend.prompts.drafting_prompts import demand_letter_prompt, plaint_prompt, brief_prompt, affidavit_prompt

class DraftingAgent:
    """
    DraftingAgent: Generates legal documents (demand letters, plaints, briefs, affidavits) using template-driven logic and prompt engineering.
    Supports context-aware drafting and human-in-the-loop review.
    Automatically saves drafts and logs events.
    """
    def __init__(self):
        self.templates = {
            'demand_letter': self._demand_letter_template,
            'plaint': self._plaint_template,
            'brief': self._brief_template,
            'affidavit': self._affidavit_template,
        }

    def draft_document(self, doc_type: str, context: Dict[str, Any]) -> str:
        if doc_type not in self.templates:
            return f"Unsupported document type: {doc_type}"
        draft = self.templates[doc_type](context)
        file_path = save_drafted_document(doc_type, draft, context)
        return f"Draft saved to: {file_path}\n\n{draft}"

    def _demand_letter_template(self, context: Dict[str, Any]) -> str:
        client = context.get('client', '[Client Name]')
        recipient = context.get('recipient', '[Recipient Name]')
        facts = context.get('facts', '[Facts of the case]')
        legal_basis = context.get('legal_basis', '[Legal basis]')
        demand = context.get('demand', '[Demand details]')
        research = context.get('research', '[Relevant research/case law]')
        return f"""
        DEMAND LETTER

        From: {client}
        To: {recipient}

        Facts: {facts}
        Legal Basis: {legal_basis}
        Research: {research}
        Demand: {demand}

        [This draft requires human review before sending.]
        """

    def _plaint_template(self, context: Dict[str, Any]) -> str:
        plaintiff = context.get('plaintiff', '[Plaintiff Name]')
        defendant = context.get('defendant', '[Defendant Name]')
        facts = context.get('facts', '[Facts of the case]')
        relief = context.get('relief', '[Relief sought]')
        research = context.get('research', '[Relevant research/case law]')
        return f"""
        PLAINT

        Plaintiff: {plaintiff}
        Defendant: {defendant}

        Facts: {facts}
        Research: {research}
        Relief Sought: {relief}

        [This draft requires human review before filing.]
        """

    def _brief_template(self, context: Dict[str, Any]) -> str:
        title = context.get('title', '[Brief Title]')
        parties = context.get('parties', '[Parties]')
        facts = context.get('facts', '[Facts of the case]')
        arguments = context.get('arguments', '[Legal arguments]')
        research = context.get('research', '[Relevant research/case law]')
        conclusion = context.get('conclusion', '[Conclusion]')
        return f"""
        LEGAL BRIEF

        Title: {title}
        Parties: {parties}
        Facts: {facts}
        Research: {research}
        Arguments: {arguments}
        Conclusion: {conclusion}

        [This draft requires human review before submission.]
        """

    def _affidavit_template(self, context: Dict[str, Any]) -> str:
        deponent = context.get('deponent', '[Deponent Name]')
        facts = context.get('facts', '[Facts sworn to]')
        research = context.get('research', '[Relevant research/case law]')
        statement = context.get('statement', '[Statement]')
        return f"""
        AFFIDAVIT

        Deponent: {deponent}
        Facts: {facts}
        Research: {research}
        Statement: {statement}

        [This draft requires human review before swearing.]
        """

    def review_document(self, doc: str) -> str:
        return f"REVIEW REQUIRED: {doc[:100]}..."