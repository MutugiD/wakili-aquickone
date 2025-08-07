from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from backend.entity_mapper.entity_mapper import EntityMapper
import json

class DynamicFormGenerator:
    """
    Generates dynamic forms based on conversation context and document requirements using EntityMapper
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000
        )
        self.entity_mapper = EntityMapper()

    def generate_form(self, document_type: str, requirements: Dict[str, Any], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a dynamic form based on document type and requirements using EntityMapper
        """
        try:
            # Get base form structure from EntityMapper
            form_structure = self.entity_mapper.generate_form_structure(document_type, extracted_info)

            if not form_structure:
                return {
                    'document_type': document_type,
                    'fields': {},
                    'field_order': [],
                    'validation_rules': {},
                    'prefilled_data': {}
                }

            # Customize fields based on requirements
            customized_fields = self._customize_fields_from_requirements(form_structure, requirements)

            # Generate additional fields based on conversation context
            additional_fields = self._generate_additional_fields(document_type, requirements, extracted_info)

            # Merge all fields
            all_fields = {**customized_fields, **additional_fields}

            # Update form structure with customized fields
            form_structure['fields'] = all_fields
            form_structure['field_order'] = self._determine_field_order(all_fields)

            return form_structure

        except Exception as e:
            print(f"Error generating form: {str(e)}")
            return {
                'document_type': document_type,
                'fields': {},
                'field_order': [],
                'validation_rules': {},
                'prefilled_data': {}
            }

    def _customize_fields_from_requirements(self, form_structure: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Customize base fields based on requirements from conversation analysis
        """
        fields = form_structure.get('fields', {}).copy()

        # Add required fields from conversation analysis
        required_fields = requirements.get('required_fields', [])
        for field in required_fields:
            if field not in fields:
                fields[field] = {
                    'type': 'text',
                    'label': field.replace('_', ' ').title(),
                    'required': True,
                    'priority': 'high',
                    'validation': {
                        'min_length': 2,
                        'max_length': 200
                    },
                    'extraction_patterns': [field.lower()]
                }

        # Mark fields as required based on conversation
        missing_fields = requirements.get('missing_fields', [])
        for field in missing_fields:
            if field in fields:
                fields[field]['required'] = True

        return fields

    def _generate_additional_fields(self, document_type: str, requirements: Dict[str, Any], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate additional fields based on conversation context using LLM
        """
        try:
            prompt = f"""
            Based on the conversation analysis, suggest additional fields that might be needed for a {document_type}.

            Extracted Information:
            {json.dumps(extracted_info, indent=2)}

            Requirements:
            {json.dumps(requirements, indent=2)}

            Suggest additional fields that might be missing. Respond with JSON:
            {{
                "additional_fields": {{
                    "field_name": {{
                        "type": "text|textarea|number|date|select",
                        "label": "Field Label",
                        "required": true/false,
                        "priority": "high|medium|low",
                        "validation": {{
                            "min_length": number,
                            "max_length": number,
                            "min": number,
                            "max": number
                        }},
                        "extraction_patterns": ["pattern1", "pattern2"],
                        "options": ["option1", "option2"] // for select fields
                    }}
                }}
            }}
            """

            response = self.llm.invoke(prompt)

            # Try to extract JSON from response
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"additional_fields": {}}

            return result.get('additional_fields', {})

        except Exception as e:
            print(f"Error generating additional fields: {str(e)}")
            return {}

    def _determine_field_order(self, fields: Dict[str, Any]) -> List[str]:
        """
        Determine the logical order of fields using EntityMapper priorities
        """
        priorities = self.entity_mapper.get_priorities()

        # Sort fields by priority
        sorted_fields = sorted(
            fields.items(),
            key=lambda x: priorities.get(x[1].get('priority', 'medium'), 2)
        )

        return [field_name for field_name, _ in sorted_fields]

    def validate_form_data(self, document_type: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate form data using EntityMapper validation rules
        """
        validation_results = {
            'is_valid': True,
            'errors': {},
            'field_errors': {}
        }

        fields = self.entity_mapper.get_document_fields(document_type)

        for field_name, value in form_data.items():
            if field_name in fields:
                validation_result = self.entity_mapper.validate_field_value(document_type, field_name, value)

                if not validation_result['valid']:
                    validation_results['is_valid'] = False
                    validation_results['field_errors'][field_name] = validation_result['errors']
                    validation_results['errors'][field_name] = validation_result['errors']

        return validation_results

    def get_document_types(self) -> Dict[str, Any]:
        """
        Get available document types from EntityMapper
        """
        return self.entity_mapper.get_document_types()

    def get_field_config(self, document_type: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get field configuration from EntityMapper
        """
        return self.entity_mapper.get_field_config(document_type, field_name)