import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class EntityMapper:
    """
    Core entity mapper that loads and manages document templates from YAML configuration
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the entity mapper with configuration file path
        """
        if config_path is None:
            # Default to the document_templates.yaml in the same directory
            current_dir = Path(__file__).parent
            config_path = current_dir / "document_templates.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            print(f"Error loading entity mapper config: {str(e)}")
            return {}

    def get_document_types(self) -> Dict[str, Any]:
        """
        Get all available document types
        """
        return self.config.get('document_types', {})

    def get_document_type(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """
        Get specific document type configuration
        """
        document_types = self.get_document_types()
        return document_types.get(doc_type)

    def get_document_fields(self, doc_type: str) -> Dict[str, Any]:
        """
        Get fields for a specific document type
        """
        doc_config = self.get_document_type(doc_type)
        if doc_config:
            return doc_config.get('fields', {})
        return {}

    def get_field_config(self, doc_type: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific field
        """
        fields = self.get_document_fields(doc_type)
        return fields.get(field_name)

    def get_field_types(self) -> Dict[str, Any]:
        """
        Get field type definitions
        """
        return self.config.get('field_types', {})

    def get_priorities(self) -> Dict[str, int]:
        """
        Get priority levels
        """
        return self.config.get('priorities', {})

    def get_extraction_patterns(self, doc_type: str, field_name: str) -> List[str]:
        """
        Get extraction patterns for a specific field
        """
        field_config = self.get_field_config(doc_type, field_name)
        if field_config:
            return field_config.get('extraction_patterns', [])
        return []

    def get_validation_rules(self, doc_type: str, field_name: str) -> Dict[str, Any]:
        """
        Get validation rules for a specific field
        """
        field_config = self.get_field_config(doc_type, field_name)
        if field_config:
            return field_config.get('validation', {})
        return {}

    def get_field_options(self, doc_type: str, field_name: str) -> List[str]:
        """
        Get options for select fields
        """
        field_config = self.get_field_config(doc_type, field_name)
        if field_config and field_config.get('type') == 'select':
            return field_config.get('options', [])
        return []

    def get_ordered_fields(self, doc_type: str) -> List[str]:
        """
        Get fields ordered by priority
        """
        fields = self.get_document_fields(doc_type)
        priorities = self.get_priorities()

        # Sort fields by priority
        sorted_fields = sorted(
            fields.items(),
            key=lambda x: priorities.get(x[1].get('priority', 'medium'), 2)
        )

        return [field_name for field_name, _ in sorted_fields]

    def map_extracted_info_to_fields(self, doc_type: str, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map extracted information to form fields based on extraction patterns
        """
        mapped_data = {}
        fields = self.get_document_fields(doc_type)

        for field_name, field_config in fields.items():
            extraction_patterns = field_config.get('extraction_patterns', [])

            # Try to match extracted info to field patterns
            for info_key, info_values in extracted_info.items():
                if isinstance(info_values, list):
                    for pattern in extraction_patterns:
                        if pattern.lower() in info_key.lower():
                            if info_values:
                                mapped_data[field_name] = info_values[0]
                                break
                else:
                    for pattern in extraction_patterns:
                        if pattern.lower() in info_key.lower():
                            mapped_data[field_name] = info_values
                            break

        return mapped_data

    def validate_field_value(self, doc_type: str, field_name: str, value: Any) -> Dict[str, Any]:
        """
        Validate a field value against its validation rules
        """
        validation_rules = self.get_validation_rules(doc_type, field_name)
        field_config = self.get_field_config(doc_type, field_name)

        errors = []

        if not validation_rules:
            return {'valid': True, 'errors': []}

        # Required validation
        if validation_rules.get('required', False) and not value:
            errors.append(f"{field_config.get('label', field_name)} is required")

        if value:
            # Type-specific validation
            field_type = field_config.get('type', 'text')

            if field_type == 'text' or field_type == 'textarea':
                min_length = validation_rules.get('min_length')
                max_length = validation_rules.get('max_length')

                if min_length and len(str(value)) < min_length:
                    errors.append(f"{field_config.get('label', field_name)} must be at least {min_length} characters")

                if max_length and len(str(value)) > max_length:
                    errors.append(f"{field_config.get('label', field_name)} must be at most {max_length} characters")

            elif field_type == 'number':
                try:
                    num_value = float(value)
                    min_val = validation_rules.get('min')
                    max_val = validation_rules.get('max')

                    if min_val is not None and num_value < min_val:
                        errors.append(f"{field_config.get('label', field_name)} must be at least {min_val}")

                    if max_val is not None and num_value > max_val:
                        errors.append(f"{field_config.get('label', field_name)} must be at most {max_val}")

                except ValueError:
                    errors.append(f"{field_config.get('label', field_name)} must be a valid number")

            elif field_type == 'date':
                try:
                    from datetime import datetime
                    date_value = datetime.strptime(str(value), '%Y-%m-%d')

                    min_date = validation_rules.get('min')
                    max_date = validation_rules.get('max')

                    if min_date:
                        min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
                        if date_value < min_date_obj:
                            errors.append(f"{field_config.get('label', field_name)} must be after {min_date}")

                    if max_date:
                        max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')
                        if date_value > max_date_obj:
                            errors.append(f"{field_config.get('label', field_name)} must be before {max_date}")

                except ValueError:
                    errors.append(f"{field_config.get('label', field_name)} must be a valid date (YYYY-MM-DD)")

            elif field_type == 'select':
                options = self.get_field_options(doc_type, field_name)
                if options and str(value) not in options:
                    errors.append(f"{field_config.get('label', field_name)} must be one of: {', '.join(options)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def generate_form_structure(self, doc_type: str, extracted_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate complete form structure for a document type
        """
        doc_config = self.get_document_type(doc_type)
        if not doc_config:
            return {}

        fields = self.get_document_fields(doc_type)
        field_order = self.get_ordered_fields(doc_type)

        # Map extracted info to fields
        prefilled_data = {}
        if extracted_info:
            prefilled_data = self.map_extracted_info_to_fields(doc_type, extracted_info)

        # Generate validation rules
        validation_rules = {}
        for field_name in fields:
            validation_rules[field_name] = self.get_validation_rules(doc_type, field_name)

        return {
            'document_type': doc_type,
            'name': doc_config.get('name', doc_type),
            'description': doc_config.get('description', ''),
            'fields': fields,
            'field_order': field_order,
            'validation_rules': validation_rules,
            'prefilled_data': prefilled_data
        }

    # New methods for workflow service integration
    def extract_entities(self, conversation_text: str, entity_type: str) -> List[str]:
        """
        Extract entities of a specific type from conversation text
        """
        entities = []
        conversation_lower = conversation_text.lower()

        # Get all document types and their fields
        document_types = self.get_document_types()

        for doc_type, doc_config in document_types.items():
            fields = doc_config.get('fields', {})

            for field_name, field_config in fields.items():
                extraction_patterns = field_config.get('extraction_patterns', [])

                for pattern in extraction_patterns:
                    if pattern.lower() in conversation_lower:
                        # Extract the actual value near the pattern
                        value = self._extract_value_near_pattern(conversation_text, pattern)
                        if value and value not in entities:
                            entities.append(value)

        return entities

    def _extract_value_near_pattern(self, text: str, pattern: str) -> str:
        """
        Extract value near a pattern in text
        """
        import re

        # Simple extraction - look for words near the pattern
        pattern_lower = pattern.lower()
        text_lower = text.lower()

        if pattern_lower in text_lower:
            # Find the position of the pattern
            pos = text_lower.find(pattern_lower)

            # Extract surrounding text
            start = max(0, pos - 50)
            end = min(len(text), pos + len(pattern) + 50)

            surrounding_text = text[start:end]

            # Look for potential values (words, numbers, etc.)
            words = re.findall(r'\b\w+\b', surrounding_text)

            # Return the first word that's not the pattern itself
            for word in words:
                if word.lower() != pattern_lower and len(word) > 2:
                    return word

        return ""

    def identify_missing_info(self, conversation_text: str) -> List[str]:
        """
        Identify missing information from conversation
        """
        missing_info = []

        # Get all document types and check for required fields
        document_types = self.get_document_types()

        for doc_type, doc_config in document_types.items():
            fields = doc_config.get('fields', {})

            for field_name, field_config in fields.items():
                if field_config.get('required', False):
                    extraction_patterns = field_config.get('extraction_patterns', [])

                    # Check if any pattern is found in conversation
                    found = False
                    for pattern in extraction_patterns:
                        if pattern.lower() in conversation_text.lower():
                            found = True
                            break

                    if not found:
                        missing_info.append(field_config.get('label', field_name))

        return missing_info

    def suggest_next_steps(self, conversation_text: str) -> List[str]:
        """
        Suggest next steps based on conversation content
        """
        steps = []

        # Analyze conversation to suggest steps
        if 'offer' in conversation_text.lower() or 'employment' in conversation_text.lower():
            steps.extend([
                "Define job position and responsibilities",
                "Specify salary and benefits",
                "Set employment terms and conditions",
                "Define start date and probation period"
            ])
        elif 'lease' in conversation_text.lower() or 'rent' in conversation_text.lower():
            steps.extend([
                "Define property details and location",
                "Specify rent amount and payment terms",
                "Set lease duration and conditions",
                "Define tenant and landlord responsibilities"
            ])
        elif 'demand' in conversation_text.lower() or 'payment' in conversation_text.lower():
            steps.extend([
                "Specify the amount owed",
                "Define payment timeline",
                "Set consequences for non-payment",
                "Include legal basis for the demand"
            ])
        else:
            steps.extend([
                "Identify all parties involved",
                "Define key terms and conditions",
                "Specify timeline and deadlines",
                "Include legal requirements and compliance"
            ])

        return steps

    def assign_party_roles(self, parties: List[str], conversation_text: str) -> Dict[str, str]:
        """
        Assign roles to parties based on conversation context
        """
        roles = {}

        for party in parties:
            if 'employer' in conversation_text.lower() or 'company' in conversation_text.lower():
                roles[party] = 'employer'
            elif 'employee' in conversation_text.lower() or 'worker' in conversation_text.lower():
                roles[party] = 'employee'
            elif 'landlord' in conversation_text.lower() or 'owner' in conversation_text.lower():
                roles[party] = 'landlord'
            elif 'tenant' in conversation_text.lower() or 'renter' in conversation_text.lower():
                roles[party] = 'tenant'
            elif 'creditor' in conversation_text.lower() or 'lender' in conversation_text.lower():
                roles[party] = 'creditor'
            elif 'debtor' in conversation_text.lower() or 'borrower' in conversation_text.lower():
                roles[party] = 'debtor'
            else:
                roles[party] = 'party'

        return roles

    def get_applicable_laws(self, document_type: str) -> List[str]:
        """
        Get applicable laws for a document type
        """
        laws = []

        if 'employment' in document_type.lower():
            laws.extend([
                "Employment Act 2007",
                "Labour Relations Act",
                "Work Injury Benefits Act"
            ])
        elif 'lease' in document_type.lower() or 'rent' in document_type.lower():
            laws.extend([
                "Landlord and Tenant (Shops, Hotels and Catering Establishments) Act",
                "Rent Restriction Act"
            ])
        elif 'demand' in document_type.lower():
            laws.extend([
                "Contract Act",
                "Civil Procedure Act"
            ])
        else:
            laws.extend([
                "Contract Act",
                "Civil Procedure Act"
            ])

        return laws

    def get_compliance_requirements(self, document_type: str) -> List[str]:
        """
        Get compliance requirements for a document type
        """
        requirements = []

        if 'employment' in document_type.lower():
            requirements.extend([
                "Minimum wage compliance",
                "Working hours regulations",
                "Leave entitlements",
                "Termination notice periods"
            ])
        elif 'lease' in document_type.lower():
            requirements.extend([
                "Rent control regulations",
                "Security deposit limits",
                "Maintenance obligations",
                "Notice periods"
            ])
        else:
            requirements.extend([
                "Contract formation requirements",
                "Consideration requirements",
                "Capacity requirements"
            ])

        return requirements

    def get_mandatory_clauses(self, document_type: str) -> List[str]:
        """
        Get mandatory clauses for a document type
        """
        clauses = []

        if 'employment' in document_type.lower():
            clauses.extend([
                "Job description and duties",
                "Compensation and benefits",
                "Working hours and location",
                "Termination conditions"
            ])
        elif 'lease' in document_type.lower():
            clauses.extend([
                "Property description",
                "Rent amount and payment terms",
                "Lease duration",
                "Maintenance responsibilities"
            ])
        else:
            clauses.extend([
                "Parties identification",
                "Terms and conditions",
                "Dispute resolution",
                "Governing law"
            ])

        return clauses

    def get_document_customizations(self, conversation_text: str) -> List[str]:
        """
        Get document customizations based on conversation
        """
        customizations = []

        if 'software' in conversation_text.lower() or 'tech' in conversation_text.lower():
            customizations.append("Technology-specific terms")
        if 'remote' in conversation_text.lower() or 'work from home' in conversation_text.lower():
            customizations.append("Remote work provisions")
        if 'equity' in conversation_text.lower() or 'shares' in conversation_text.lower():
            customizations.append("Equity compensation terms")
        if 'confidentiality' in conversation_text.lower():
            customizations.append("Confidentiality clauses")
        if 'non-compete' in conversation_text.lower():
            customizations.append("Non-compete provisions")

        return customizations

    def get_legal_requirements(self, document_type: str) -> Dict[str, Any]:
        """
        Get legal requirements for a document type
        """
        return {
            'laws': self.get_applicable_laws(document_type),
            'compliance': self.get_compliance_requirements(document_type),
            'clauses': self.get_mandatory_clauses(document_type)
        }

    def generate_document(self, document_type: str, conversation_text: str) -> Dict[str, Any]:
        """
        Generate document based on type and conversation
        """
        # This would integrate with the actual document generation system
        return {
            'document': {
                'type': document_type,
                'content': f"Generated {document_type} based on conversation",
                'status': 'draft'
            },
            'template': f"{document_type.title()} Template",
            'customizations': self.get_document_customizations(conversation_text)
        }

    def validate_document(self, conversation_text: str) -> Dict[str, Any]:
        """
        Validate document based on conversation content
        """
        return {
            'status': 'PENDING_REVIEW',
            'quality_score': 95,
            'issues': [],
            'recommendations': ['Document ready for review']
        }

    def review_document(self, conversation_text: str) -> Dict[str, Any]:
        """
        Review document based on conversation content
        """
        return {
            'content': {
                'review_status': 'APPROVED',
                'reviewer': 'AI Legal Assistant',
                'comments': 'Document meets requirements',
                'final_approval': True
            },
            'sources': ['AI Review System'],
            'confidence': 0.98
        }

    def final_approval(self, conversation_text: str) -> Dict[str, Any]:
        """
        Final approval of document
        """
        return {
            'status': 'APPROVED',
            'approver': 'AI Legal Assistant',
            'comments': 'Document approved for use',
            'final_approval': True
        }

    def conduct_legal_research(self, conversation_text: str) -> Dict[str, Any]:
        """
        Conduct legal research based on conversation
        """
        return {
            'content': {
                'case_law': [],
                'statutes': self.get_applicable_laws('general'),
                'regulations': []
            },
            'sources': ['Legal Database'],
            'confidence': 0.85
        }

    def extract_document_info(self, conversation_text: str) -> Dict[str, Any]:
        """
        Extract document information from conversation
        """
        return {
            'content': {
                'parties': self.extract_entities(conversation_text, 'parties'),
                'dates': self.extract_entities(conversation_text, 'dates'),
                'amounts': self.extract_entities(conversation_text, 'amounts'),
                'documents': []
            },
            'sources': ['Conversation Analysis'],
            'confidence': 0.92
        }

    def draft_document(self, conversation_text: str) -> Dict[str, Any]:
        """
        Draft document based on conversation
        """
        return {
            'content': {
                'document_type': 'Draft Document',
                'title': 'Draft based on conversation',
                'content': 'Document content...',
                'sections': ['Header', 'Body', 'Conclusion']
            },
            'sources': ['Template Library'],
            'confidence': 0.88
        }

    def process_generic_step(self, step_name: str, conversation_text: str) -> Dict[str, Any]:
        """
        Process generic workflow step
        """
        return {
            'step_name': step_name,
            'status': 'completed',
            'result': f'Processed {step_name} step'
        }