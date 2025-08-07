"""
Dynamic Form Generator
Creates forms dynamically based on any document schema
"""

import re
from typing import Dict, List, Any, Optional
from .dynamic_schema_loader import DynamicSchemaLoader

class DynamicFormGenerator:
    """
    Generates dynamic forms based on document schemas
    No hardcoding - works with any document type
    """
    
    def __init__(self):
        self.schema_loader = DynamicSchemaLoader()
    
    def generate_form_from_conversation(self, conversation: str) -> Dict[str, Any]:
        """
        Generate a complete form based on conversation context
        This is the main entry point for dynamic form generation
        """
        
        # Create dynamic schema from conversation
        document_type = self._detect_document_type(conversation)
        schema = self.schema_loader.create_dynamic_schema(document_type, conversation)
        
        # Extract information from conversation
        extracted_info = self._extract_information_from_conversation(conversation, schema)
        
        # Generate form structure
        form_structure = self._generate_form_structure(schema, extracted_info)
        
        # Generate validation rules
        validation_rules = self._generate_validation_rules(schema)
        
        # Generate user interaction flow
        interaction_flow = self._generate_interaction_flow(schema, extracted_info)
        
        return {
            'document_type': document_type,
            'schema': schema,
            'form_structure': form_structure,
            'validation_rules': validation_rules,
            'interaction_flow': interaction_flow,
            'extracted_info': extracted_info,
            'missing_info': self._identify_missing_info(schema, extracted_info)
        }
    
    def _detect_document_type(self, conversation: str) -> str:
        """Detect document type from conversation"""
        conversation_lower = conversation.lower()
        
        if any(word in conversation_lower for word in ['employment', 'employee', 'employer', 'job', 'work']):
            return 'employment_contract'
        elif any(word in conversation_lower for word in ['lease', 'rent', 'tenant', 'landlord', 'property']):
            return 'lease_agreement'
        elif any(word in conversation_lower for word in ['partnership', 'business', 'company', 'venture']):
            return 'partnership_agreement'
        elif any(word in conversation_lower for word in ['service', 'consulting', 'freelance', 'contractor']):
            return 'service_agreement'
        elif any(word in conversation_lower for word in ['demand', 'payment', 'debt', 'owed']):
            return 'demand_letter'
        elif any(word in conversation_lower for word in ['court', 'plaint', 'lawsuit', 'case']):
            return 'plaint'
        elif any(word in conversation_lower for word in ['affidavit', 'sworn', 'statement', 'witness']):
            return 'affidavit'
        else:
            return 'custom_document'
    
    def _extract_information_from_conversation(self, conversation: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract information from conversation using schema patterns"""
        extracted_info = {}
        
        # Extract party information
        if 'field_discovery' in schema and 'parties' in schema['field_discovery']:
            for party_field in schema['field_discovery']['parties']:
                pattern = party_field['pattern']
                matches = re.findall(pattern, conversation, re.IGNORECASE)
                if matches:
                    # Extract names near the party keywords
                    party_info = self._extract_party_details(conversation, pattern)
                    if party_info:
                        extracted_info[party_field['role']] = party_info
        
        # Extract other fields based on patterns
        for category, fields in schema.get('field_discovery', {}).items():
            if category != 'parties':
                for field in fields:
                    pattern = field['pattern']
                    matches = re.findall(pattern, conversation, re.IGNORECASE)
                    if matches:
                        # Extract values near the keywords
                        value = self._extract_field_value(conversation, pattern, field['field_type'])
                        if value:
                            extracted_info[category] = value
        
        return extracted_info
    
    def _extract_party_details(self, conversation: str, party_pattern: str) -> Dict[str, str]:
        """Extract party details from conversation"""
        # Look for names near party keywords
        lines = conversation.split('\n')
        party_info = {}
        
        for line in lines:
            if re.search(party_pattern, line, re.IGNORECASE):
                # Extract name patterns
                name_patterns = [
                    r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
                    r'([A-Z][a-z]+)',  # Single name
                    r'([A-Z][A-Z\s]+)',  # ALL CAPS
                ]
                
                for pattern in name_patterns:
                    names = re.findall(pattern, line)
                    if names:
                        party_info['name'] = names[0].strip()
                        break
                
                # Extract address patterns
                address_patterns = [
                    r'(\d+\s+[A-Za-z\s]+(?:Street|Road|Avenue|Lane|Drive))',
                    r'(P\.?O\.?\s*Box\s+\d+)',
                ]
                
                for pattern in address_patterns:
                    addresses = re.findall(pattern, line)
                    if addresses:
                        party_info['address'] = addresses[0].strip()
                        break
        
        return party_info
    
    def _extract_field_value(self, conversation: str, pattern: str, field_type: str) -> Any:
        """Extract field value based on type"""
        lines = conversation.split('\n')
        
        for line in lines:
            if re.search(pattern, line, re.IGNORECASE):
                if field_type == 'currency':
                    # Extract currency amounts
                    amount_pattern = r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:shillings?|ksh|usd|dollars?)'
                    amounts = re.findall(amount_pattern, line, re.IGNORECASE)
                    if amounts:
                        return amounts[0]
                
                elif field_type == 'date':
                    # Extract dates
                    date_patterns = [
                        r'(\d{1,2}/\d{1,2}/\d{4})',
                        r'(\d{4}-\d{2}-\d{2})',
                        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
                    ]
                    for date_pattern in date_patterns:
                        dates = re.findall(date_pattern, line, re.IGNORECASE)
                        if dates:
                            return dates[0]
                
                elif field_type == 'duration':
                    # Extract durations
                    duration_pattern = r'(\d+)\s*(?:months?|years?|weeks?|days?)'
                    durations = re.findall(duration_pattern, line, re.IGNORECASE)
                    if durations:
                        return durations[0]
                
                else:
                    # Extract text after the pattern
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        # Get text after the match
                        after_match = line[match.end():].strip()
                        if after_match:
                            return after_match
        
        return None
    
    def _generate_form_structure(self, schema: Dict[str, Any], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate form structure based on schema"""
        form_structure = {
            'fields': {},
            'field_order': [],
            'sections': []
        }
        
        # Generate fields based on schema
        for category, fields in schema.get('field_discovery', {}).items():
            section = {
                'name': category.replace('_', ' ').title(),
                'fields': []
            }
            
            for field in fields:
                field_name = f"{category}_{field.get('role', 'value')}"
                field_config = self._create_field_config(field, extracted_info)
                
                form_structure['fields'][field_name] = field_config
                section['fields'].append(field_name)
                form_structure['field_order'].append(field_name)
            
            form_structure['sections'].append(section)
        
        return form_structure
    
    def _create_field_config(self, field: Dict[str, Any], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create field configuration"""
        field_type = field.get('field_type', 'text')
        
        config = {
            'type': self._map_field_type(field_type),
            'label': field.get('role', 'value').replace('_', ' ').title(),
            'required': field.get('validation') == 'required',
            'priority': field.get('priority', 'medium'),
            'validation': self._get_validation_rules(field_type),
            'extraction_patterns': [field.get('pattern', '')]
        }
        
        # Add field-specific options
        if field_type == 'select':
            config['options'] = self._get_select_options(field)
        
        # Add prefilled value if available
        if field.get('role') in extracted_info:
            config['prefilled_value'] = extracted_info[field['role']]
        
        return config
    
    def _map_field_type(self, schema_type: str) -> str:
        """Map schema field type to form field type"""
        type_mapping = {
            'text': 'text',
            'textarea': 'textarea',
            'number': 'number',
            'date': 'date',
            'select': 'select',
            'boolean': 'select',
            'currency': 'number',
            'duration': 'number',
            'party': 'text'
        }
        return type_mapping.get(schema_type, 'text')
    
    def _get_validation_rules(self, field_type: str) -> Dict[str, Any]:
        """Get validation rules for field type"""
        rules = {}
        
        if field_type == 'text':
            rules = {
                'min_length': 2,
                'max_length': 100
            }
        elif field_type == 'textarea':
            rules = {
                'min_length': 10,
                'max_length': 1000
            }
        elif field_type == 'number':
            rules = {
                'min': 0,
                'max': 999999999
            }
        elif field_type == 'currency':
            rules = {
                'min': 0,
                'max': 999999999
            }
        elif field_type == 'date':
            rules = {
                'min': '1900-01-01',
                'max': '2100-12-31'
            }
        
        return rules
    
    def _get_select_options(self, field: Dict[str, Any]) -> List[str]:
        """Get select options for field"""
        if field.get('field_type') == 'boolean':
            return ['Yes', 'No']
        
        # Default options based on field role
        role = field.get('role', '')
        if 'type' in role:
            return ['Standard', 'Custom', 'Other']
        elif 'status' in role:
            return ['Active', 'Inactive', 'Pending']
        
        return ['Option 1', 'Option 2', 'Option 3']
    
    def _generate_validation_rules(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation rules"""
        return {
            'required_fields': self._get_required_fields(schema),
            'business_rules': schema.get('validation', {}).get('business_logic', []),
            'legal_requirements': schema.get('validation', {}).get('legal_requirements', [])
        }
    
    def _get_required_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Get list of required fields"""
        required_fields = []
        
        for category, fields in schema.get('field_discovery', {}).items():
            for field in fields:
                if field.get('validation') == 'required':
                    field_name = f"{category}_{field.get('role', 'value')}"
                    required_fields.append(field_name)
        
        return required_fields
    
    def _generate_interaction_flow(self, schema: Dict[str, Any], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user interaction flow"""
        return {
            'stages': schema.get('review_workflow', {}).get('stages', []),
            'questions': schema.get('user_interaction', {}).get('information_gathering', []),
            'validation_questions': schema.get('user_interaction', {}).get('validation_questions', []),
            'final_confirmation': schema.get('user_interaction', {}).get('final_confirmation', [])
        }
    
    def _identify_missing_info(self, schema: Dict[str, Any], extracted_info: Dict[str, Any]) -> List[str]:
        """Identify missing information"""
        missing_info = []
        
        # Check required fields
        for category, fields in schema.get('field_discovery', {}).items():
            for field in fields:
                if field.get('validation') == 'required':
                    field_name = f"{category}_{field.get('role', 'value')}"
                    if field_name not in extracted_info:
                        missing_info.append(field_name)
        
        return missing_info
    
    def update_form_with_user_input(self, form_data: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Update form with user input and generate next questions"""
        updated_form = form_data.copy()
        
        # Update extracted info with user input
        updated_form['extracted_info'].update(user_input)
        
        # Re-identify missing info
        updated_form['missing_info'] = self._identify_missing_info(
            updated_form['schema'], 
            updated_form['extracted_info']
        )
        
        # Generate next questions based on missing info
        next_questions = self._generate_next_questions(updated_form['missing_info'], updated_form['schema'])
        updated_form['next_questions'] = next_questions
        
        return updated_form
    
    def _generate_next_questions(self, missing_info: List[str], schema: Dict[str, Any]) -> List[str]:
        """Generate questions for missing information"""
        questions = []
        
        for field_name in missing_info:
            category, field_type = field_name.split('_', 1)
            
            if 'employer' in field_name or 'employee' in field_name:
                questions.append(f"What is the {field_type.replace('_', ' ')} name and details?")
            elif 'salary' in field_name or 'payment' in field_name:
                questions.append("What is the agreed salary/compensation amount?")
            elif 'duration' in field_name or 'period' in field_name:
                questions.append("What is the contract duration/period?")
            elif 'start' in field_name or 'commencement' in field_name:
                questions.append("What is the start/commencement date?")
            else:
                questions.append(f"Please provide {field_name.replace('_', ' ')}")
        
        return questions 