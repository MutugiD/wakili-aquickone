from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
import os
import json
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class InteractiveDraftingAgent:
    """
    Interactive Drafting Agent: Provides step-by-step document creation with real-time validation
    and user feedback integration. Supports collaborative document refinement.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
            temperature=0.1,
            max_tokens=4000
        )
        self.document_configs = self._load_document_configurations()

    def get_document_requirements(self, doc_type: str) -> Dict[str, Any]:
        """
        Get document type requirements and form fields
        """
        config = self.document_configs.get(doc_type, {})
        return {
            "fields": config.get("fields", []),
            "validation_rules": config.get("validation_rules", []),
            "estimated_time": config.get("estimated_time", "15-20 minutes"),
            "complexity": config.get("complexity", "medium")
        }

    def validate_information(self, doc_type: str, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user-provided information for document type
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        config = self.document_configs.get(doc_type, {})
        fields = config.get("fields", [])

        for field in fields:
            field_id = field.get("id")
            required = field.get("required", False)
            field_value = information.get(field_id, "")

            # Required field validation
            if required and not field_value:
                validation_result["is_valid"] = False
                validation_result["errors"].append({
                    "field": field_id,
                    "message": f"{field.get('label', field_id)} is required",
                    "type": "required"
                })

            # Min length validation
            min_length = field.get("min_length")
            if min_length and len(str(field_value)) < min_length:
                validation_result["warnings"].append({
                    "field": field_id,
                    "message": f"{field.get('label', field_id)} should be at least {min_length} characters",
                    "type": "min_length"
                })

        return validation_result

    def generate_document_preview(self, doc_type: str, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate document preview with current information
        """
        try:
            # Build context from user information
            context = self._build_context_from_information(doc_type, information)

            # Generate document content using LLM
            prompt = self._get_drafting_prompt(doc_type, context)
            response = self.llm.invoke(prompt)
            raw_content = response.content

            # Create preview sections
            sections = self._create_preview_sections(raw_content, doc_type)

            # Validate the generated content
            validation_result = self.validate_information(doc_type, information)

            return {
                "success": True,
                "sections": sections,
                "validation": validation_result,
                "context": context,
                "raw_content": raw_content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sections": []
            }

    def process_user_feedback(self, document_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback and generate refined document
        """
        try:
            # Extract feedback details
            section_id = feedback.get("section_id")
            feedback_text = feedback.get("feedback")
            feedback_type = feedback.get("type", "content")

            # Generate refined content based on feedback
            refinement_prompt = f"""
            The user provided feedback on section '{section_id}': {feedback_text}
            Feedback type: {feedback_type}

            Please refine the document content based on this feedback.
            """

            response = self.llm.invoke(refinement_prompt)
            refined_content = response.content

            return {
                "success": True,
                "refined_content": refined_content,
                "feedback_processed": feedback
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def export_document(self, document_id: str, format: str, content: str) -> str:
        """
        Export document in specified format
        """
        try:
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(exports_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{document_id}_{timestamp}"

            if format == "txt":
                file_path = os.path.join(exports_dir, f"{filename}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif format == "html":
                file_path = os.path.join(exports_dir, f"{filename}.html")
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Legal Document</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        .document {{ max-width: 800px; margin: 0 auto; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .content {{ white-space: pre-wrap; }}
                    </style>
                </head>
                <body>
                    <div class="document">
                        <div class="header">
                            <h1>Legal Document</h1>
                            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                        </div>
                        <div class="content">{content}</div>
                    </div>
                </body>
                </html>
                """
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                # Default to txt
                file_path = os.path.join(exports_dir, f"{filename}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            return file_path

        except Exception as e:
            raise Exception(f"Failed to export document: {str(e)}")

    def save_document(self, document_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """
        Save document with metadata
        """
        try:
            # Create documents directory if it doesn't exist
            documents_dir = os.path.join(os.getcwd(), "documents")
            os.makedirs(documents_dir, exist_ok=True)

            # Save document content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{document_id}_{timestamp}.json"
            file_path = os.path.join(documents_dir, filename)

            document_data = {
                "id": document_id,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, indent=2, ensure_ascii=False)

            return file_path

        except Exception as e:
            raise Exception(f"Failed to save document: {str(e)}")

    def _load_document_configurations(self) -> Dict[str, Any]:
        """
        Load document type configurations
        """
        return {
            "demand_letter": {
                "fields": [
                    {
                        "id": "client_name",
                        "label": "Client Name",
                        "type": "text",
                        "required": True,
                        "min_length": 2
                    },
                    {
                        "id": "recipient_name",
                        "label": "Recipient Name",
                        "type": "text",
                        "required": True,
                        "min_length": 2
                    },
                    {
                        "id": "recipient_address",
                        "label": "Recipient Address",
                        "type": "textarea",
                        "required": True,
                        "min_length": 10
                    },
                    {
                        "id": "facts",
                        "label": "Factual Background",
                        "type": "textarea",
                        "required": True,
                        "min_length": 50
                    },
                    {
                        "id": "legal_basis",
                        "label": "Legal Basis",
                        "type": "textarea",
                        "required": True,
                        "min_length": 30
                    },
                    {
                        "id": "demand",
                        "label": "Specific Demand",
                        "type": "textarea",
                        "required": True,
                        "min_length": 20
                    },
                    {
                        "id": "deadline",
                        "label": "Response Deadline",
                        "type": "date",
                        "required": False
                    }
                ],
                "estimated_time": "10-15 minutes",
                "complexity": "simple"
            },
            "plaint": {
                "fields": [
                    {
                        "id": "plaintiff_name",
                        "label": "Plaintiff Name",
                        "type": "text",
                        "required": True,
                        "min_length": 2
                    },
                    {
                        "id": "defendant_name",
                        "label": "Defendant Name",
                        "type": "text",
                        "required": True,
                        "min_length": 2
                    },
                    {
                        "id": "court_name",
                        "label": "Court Name",
                        "type": "text",
                        "required": True,
                        "min_length": 5
                    },
                    {
                        "id": "case_number",
                        "label": "Case Number (if available)",
                        "type": "text",
                        "required": False
                    },
                    {
                        "id": "facts",
                        "label": "Factual Allegations",
                        "type": "textarea",
                        "required": True,
                        "min_length": 100
                    },
                    {
                        "id": "causes_of_action",
                        "label": "Causes of Action",
                        "type": "textarea",
                        "required": True,
                        "min_length": 50
                    },
                    {
                        "id": "relief_sought",
                        "label": "Relief Sought",
                        "type": "textarea",
                        "required": True,
                        "min_length": 30
                    }
                ],
                "estimated_time": "20-30 minutes",
                "complexity": "medium"
            },
            "affidavit": {
                "fields": [
                    {
                        "id": "deponent_name",
                        "label": "Deponent Name",
                        "type": "text",
                        "required": True,
                        "min_length": 2
                    },
                    {
                        "id": "deponent_address",
                        "label": "Deponent Address",
                        "type": "textarea",
                        "required": True,
                        "min_length": 10
                    },
                    {
                        "id": "capacity",
                        "label": "Capacity/Relationship to Case",
                        "type": "text",
                        "required": True,
                        "min_length": 5
                    },
                    {
                        "id": "statement",
                        "label": "Sworn Statement",
                        "type": "textarea",
                        "required": True,
                        "min_length": 100
                    },
                    {
                        "id": "supporting_documents",
                        "label": "Supporting Documents",
                        "type": "textarea",
                        "required": False
                    }
                ],
                "estimated_time": "15-20 minutes",
                "complexity": "simple"
            }
        }

    def _build_context_from_information(self, doc_type: str, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build context from user information
        """
        context = {
            "document_type": doc_type,
            "timestamp": datetime.now().isoformat(),
            "user_information": information
        }

        # Add document-specific context
        if doc_type == "demand_letter":
            context.update({
                "client": information.get("client_name", ""),
                "recipient": information.get("recipient_name", ""),
                "recipient_address": information.get("recipient_address", ""),
                "facts": information.get("facts", ""),
                "legal_basis": information.get("legal_basis", ""),
                "demand": information.get("demand", ""),
                "deadline": information.get("deadline", "")
            })
        elif doc_type == "plaint":
            context.update({
                "plaintiff": information.get("plaintiff_name", ""),
                "defendant": information.get("defendant_name", ""),
                "court": information.get("court_name", ""),
                "case_number": information.get("case_number", ""),
                "facts": information.get("facts", ""),
                "causes_of_action": information.get("causes_of_action", ""),
                "relief_sought": information.get("relief_sought", "")
            })
        elif doc_type == "affidavit":
            context.update({
                "deponent": information.get("deponent_name", ""),
                "deponent_address": information.get("deponent_address", ""),
                "capacity": information.get("capacity", ""),
                "statement": information.get("statement", ""),
                "supporting_documents": information.get("supporting_documents", "")
            })

        return context

    def _get_drafting_prompt(self, doc_type: str, context: Dict[str, Any]) -> str:
        """
        Generate drafting prompt based on document type and context
        """
        base_prompts = {
            "demand_letter": """
            You are a legal professional drafting a demand letter. Create a professional demand letter with the following information:

            Client: {client}
            Recipient: {recipient}
            Recipient Address: {recipient_address}
            Facts: {facts}
            Legal Basis: {legal_basis}
            Demand: {demand}
            Deadline: {deadline}

            Format the letter professionally with proper legal structure, clear demands, and appropriate tone.
            """,
            "plaint": """
            You are a legal professional drafting a plaint (civil complaint). Create a professional plaint with the following information:

            Plaintiff: {plaintiff}
            Defendant: {defendant}
            Court: {court}
            Case Number: {case_number}
            Facts: {facts}
            Causes of Action: {causes_of_action}
            Relief Sought: {relief_sought}

            Format the plaint according to Kenyan court requirements with proper structure, numbered paragraphs, and legal formatting.
            """,
            "affidavit": """
            You are a legal professional drafting an affidavit. Create a professional affidavit with the following information:

            Deponent: {deponent}
            Deponent Address: {deponent_address}
            Capacity: {capacity}
            Statement: {statement}
            Supporting Documents: {supporting_documents}

            Format the affidavit as a sworn statement with proper legal structure and formatting for Kenyan courts.
            """
        }

        prompt_template = base_prompts.get(doc_type, "")
        return prompt_template.format(**context)

    def _create_preview_sections(self, content: str, doc_type: str) -> List[Dict[str, Any]]:
        """
        Create preview sections from document content
        """
        sections = []

        # Split content into logical sections
        lines = content.split('\n')
        current_section = {"id": "main", "title": "Document Content", "content": "", "editable": True}

        for line in lines:
            if line.strip().startswith(('#', '##', '###', '**', 'DEMAND LETTER', 'PLAINT', 'AFFIDAVIT')):
                # Save current section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)

                # Start new section
                section_title = line.strip().replace('#', '').replace('*', '').strip()
                current_section = {
                    "id": f"section_{len(sections)}",
                    "title": section_title,
                    "content": "",
                    "editable": True
                }
            else:
                current_section["content"] += line + "\n"

        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)

        # If no sections were created, create a single section
        if not sections:
            sections = [{
                "id": "main",
                "title": "Document Content",
                "content": content,
                "editable": True
            }]

        return sections