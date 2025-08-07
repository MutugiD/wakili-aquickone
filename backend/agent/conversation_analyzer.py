from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from backend.entity_mapper.entity_mapper import EntityMapper
from backend.entity_mapper.dynamic_form_generator import DynamicFormGenerator
import re
import json

class ConversationAnalyzer:
    """
    Analyzes chat conversations to detect document creation intent and extract requirements using EntityMapper
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000
        )
        self.entity_mapper = EntityMapper()
        self.dynamic_form_generator = DynamicFormGenerator()

        # Build document patterns from EntityMapper
        self.document_patterns = self._build_document_patterns()

    def _build_document_patterns(self) -> Dict[str, List[str]]:
        """
        Build document patterns from EntityMapper configuration
        """
        patterns = {}
        document_types = self.entity_mapper.get_document_types()

        for doc_type, doc_config in document_types.items():
            patterns[doc_type] = []

            # Add document type name patterns
            doc_name = doc_config.get('name', doc_type)
            patterns[doc_type].extend([
                doc_name.lower(),
                doc_type.lower(),
                doc_name.lower().replace(' ', '_'),
                doc_name.lower().replace(' ', '')
            ])

            # Add patterns from field extraction patterns
            fields = doc_config.get('fields', {})
            for field_name, field_config in fields.items():
                extraction_patterns = field_config.get('extraction_patterns', [])
                patterns[doc_type].extend(extraction_patterns)

        return patterns

    def _build_dynamic_mapping(self) -> Dict[str, str]:
        """
        Build dynamic document type mapping based on EntityMapper keywords
        """
        mapping = {}
        document_types = self.entity_mapper.get_document_types()

        for doc_type, doc_config in document_types.items():
            # Get keywords from the document config
            keywords = doc_config.get('keywords', [])
            doc_name = doc_config.get('name', doc_type)

            # Create mappings for each keyword and the document name
            for keyword in keywords:
                mapping[keyword.lower()] = doc_type

            # Also map the document name itself
            mapping[doc_name.lower()] = doc_type
            mapping[doc_type.lower()] = doc_type

        return mapping

    def analyze_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conversation to detect document creation intent
        """
        try:
            # Extract conversation text
            conversation_text = self._extract_conversation_text(messages)

            # Detect document intent
            document_intent = self._detect_document_intent(conversation_text)

            if document_intent['has_intent']:
                # Extract requirements
                requirements = self._extract_requirements(conversation_text, document_intent['document_type'])

                return {
                    'has_document_intent': True,
                    'document_type': document_intent['document_type'],
                    'confidence': document_intent['confidence'],
                    'requirements': requirements,
                    'extracted_info': self._extract_key_information(conversation_text, document_intent['document_type'])
                }
            else:
                return {
                    'has_document_intent': False,
                    'document_type': None,
                    'confidence': 0.0,
                    'requirements': {},
                    'extracted_info': {}
                }

        except Exception as e:
            print(f"Error analyzing conversation: {str(e)}")
            return {
                'has_document_intent': False,
                'document_type': None,
                'confidence': 0.0,
                'requirements': {},
                'extracted_info': {}
            }

    def generate_dynamic_form(self, conversation_text: str) -> Dict[str, Any]:
        """
        Generate a dynamic form based on conversation context
        This uses the new dynamic system instead of hardcoded templates
        """
        try:
            return self.dynamic_form_generator.generate_form_from_conversation(conversation_text)
        except Exception as e:
            print(f"Error generating dynamic form: {str(e)}")
            return {
                'document_type': 'custom_document',
                'schema': {},
                'form_structure': {'fields': {}, 'field_order': [], 'sections': []},
                'validation_rules': {},
                'interaction_flow': {},
                'extracted_info': {},
                'missing_info': []
            }

    def _extract_conversation_text(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extract conversation text from messages
        """
        conversation_parts = []

        for message in messages:
            if message.get('role') in ['user', 'human']:
                content = message.get('content', '')
                # Ensure content is not None
                if content is None:
                    content = ""
                conversation_parts.append(f"User: {content}")
            elif message.get('role') in ['assistant', 'ai']:
                content = message.get('content', '')
                # Ensure content is not None
                if content is None:
                    content = ""
                conversation_parts.append(f"Assistant: {content}")

        return "\n".join(conversation_parts)

    def _detect_document_intent(self, conversation_text: str) -> Dict[str, Any]:
        """
        Detect if user wants to create a document using intelligent analysis
        """
        conversation_lower = conversation_text.lower()

        # Check for explicit document creation requests
        explicit_document_keywords = [
            'create', 'draft', 'write', 'prepare', 'generate', 'make',
            'help me create', 'help me draft', 'please create', 'please draft',
            'need a', 'want a', 'require a', 'looking for a'
        ]

        # Dynamic document type mapping based on EntityMapper keywords
        document_type_mapping = self._build_dynamic_mapping()

        # Check if user is explicitly asking for document creation
        has_explicit_request = any(keyword in conversation_lower for keyword in explicit_document_keywords)

        if has_explicit_request:
            # First, try to detect document type using LLM intelligence
            llm_detection = self._detect_document_type_with_llm(conversation_text)

            if llm_detection and llm_detection.get('confidence', 0) > 0.5:
                return {
                    'has_intent': True,
                    'document_type': llm_detection['document_type'],
                    'confidence': llm_detection['confidence'],
                    'explicit': True,
                    'detection_method': 'llm_intelligence',
                    'search_required': llm_detection.get('search_required', True)
                }

                        # Try to find document type in the conversation using dynamic mapping
            conversation_lower = conversation_text.lower()
            detected_doc_type = None

            # Check for exact matches in the mapping
            for keyword, doc_type in document_type_mapping.items():
                if keyword in conversation_lower:
                    detected_doc_type = doc_type
                    break

            # If we found a document type, use it
            if detected_doc_type:
                return {
                    'has_intent': True,
                    'document_type': detected_doc_type,
                    'confidence': 0.8,
                    'explicit': True,
                    'detection_method': 'keyword_mapping'
                }

            # Fallback to EntityMapper for pattern-based detection
            detected_document = self._detect_document_type_from_entity_mapper(conversation_text)

            if detected_document:
                return {
                    'has_intent': True,
                    'document_type': detected_document['type'],
                    'confidence': detected_document.get('confidence', 0.6),
                    'explicit': True,
                    'detection_method': 'entity_mapper'
                }

        # No document intent detected
        return {'has_intent': False, 'document_type': None, 'confidence': 0.0}

    def _detect_document_type_with_llm(self, conversation_text: str) -> Dict[str, Any]:
        """
        Use LLM to intelligently detect document type and determine if internet search is needed
        """
        try:
            prompt = f"""
            Analyze this conversation and determine what type of document the user wants to create.

            Conversation: {conversation_text}

            Respond with JSON:
            {{
                "document_type": "specific document type (e.g., 'employment contract', 'offer letter', 'bulk water acquisition contract')",
                "confidence": 0.0-1.0,
                "search_required": true/false,
                "reasoning": "brief explanation of why this document type was detected",
                "is_common_document": true/false
            }}

            Rules:
            - Use the exact document type name from the conversation
            - If the document type is not found in available templates, use "custom_document"
            - For common legal documents, set search_required to true

            Rules:
            - If it's a common document type (employment contract, offer letter, lease agreement, etc.), set search_required to true
            - If it's a very specific/rare document type, set search_required to true
            - If it's a generic document request, set search_required to true
            - Only set search_required to false if it's a very basic document that doesn't need templates
            """

            response = self.llm.invoke(prompt)

            try:
                result = json.loads(response.content)
                return {
                    'document_type': result.get('document_type', 'custom_document'),
                    'confidence': result.get('confidence', 0.5),
                    'search_required': result.get('search_required', True),
                    'reasoning': result.get('reasoning', ''),
                    'is_common_document': result.get('is_common_document', True)
                }
            except json.JSONDecodeError:
                # Fallback parsing
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        'document_type': result.get('document_type', 'custom_document'),
                        'confidence': result.get('confidence', 0.5),
                        'search_required': result.get('search_required', True),
                        'reasoning': result.get('reasoning', ''),
                        'is_common_document': result.get('is_common_document', True)
                    }
                else:
                    return None

        except Exception as e:
            print(f"Error in LLM document detection: {str(e)}")
            return None

    def _detect_document_type_from_entity_mapper(self, conversation_text: str) -> Dict[str, Any]:
        """
        Use EntityMapper to dynamically detect document type from conversation
        """
        try:
            # Get all available document types from EntityMapper
            document_types = self.entity_mapper.get_document_types()
            conversation_lower = conversation_text.lower()

            best_match = None
            highest_confidence = 0.0

            for doc_type, doc_config in document_types.items():
                confidence = self._calculate_document_type_confidence(
                    conversation_text, doc_type, doc_config
                )

                if confidence > highest_confidence and confidence > 0.3:  # Minimum threshold
                    highest_confidence = confidence
                    best_match = {
                        'type': doc_type,
                        'confidence': confidence,
                        'config': doc_config
                    }

            return best_match

        except Exception as e:
            print(f"Error detecting document type from EntityMapper: {str(e)}")
            return None

    def _calculate_document_type_confidence(self, conversation_text: str, doc_type: str, doc_config: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a document type based on conversation content
        """
        conversation_lower = conversation_text.lower()
        confidence = 0.0

        # Check document name patterns
        doc_name = doc_config.get('name', doc_type)
        name_patterns = [
            doc_name.lower(),
            doc_type.lower(),
            doc_name.lower().replace(' ', '_'),
            doc_name.lower().replace(' ', '')
        ]

        for pattern in name_patterns:
            if pattern in conversation_lower:
                confidence += 0.3
                break

        # Check field extraction patterns
        fields = doc_config.get('fields', {})
        pattern_matches = 0
        total_patterns = 0

        for field_name, field_config in fields.items():
            extraction_patterns = field_config.get('extraction_patterns', [])
            total_patterns += len(extraction_patterns)

            for pattern in extraction_patterns:
                if pattern.lower() in conversation_lower:
                    pattern_matches += 1

        if total_patterns > 0:
            pattern_confidence = (pattern_matches / total_patterns) * 0.4
            confidence += pattern_confidence

        # Check for document-specific keywords
        keywords = doc_config.get('keywords', [])
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in conversation_lower)
        if keywords:
            keyword_confidence = min(keyword_matches / len(keywords), 1.0) * 0.3
            confidence += keyword_confidence

        return min(confidence, 1.0)

    def _llm_classify_document(self, conversation_text: str, detected_type: str) -> Dict[str, Any]:
        """
        Use LLM to classify document type and confidence
        """
        try:
            prompt = f"""
            Analyze this conversation and determine if the user wants to create a {detected_type}.

            Conversation:
            {conversation_text}

            Respond with JSON:
            {{
                "wants_to_create": true/false,
                "confidence": 0.0-1.0,
                "reasoning": "brief explanation"
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
                    # Fallback to default values
                    result = {
                        'wants_to_create': True,
                        'confidence': 0.7,
                        'reasoning': 'Pattern matched, LLM response parsing failed'
                    }

            return {
                'confidence': result.get('confidence', 0.0),
                'reasoning': result.get('reasoning', '')
            }

        except Exception as e:
            print(f"Error in LLM classification: {str(e)}")
            return {'confidence': 0.5, 'reasoning': 'LLM classification failed'}

    def _extract_requirements(self, conversation_text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract document requirements from conversation using EntityMapper
        """
        try:
            # Get field configurations from EntityMapper
            fields = self.entity_mapper.get_document_fields(document_type)
            required_fields = []
            extracted_info = {}
            missing_fields = []

            # Check each field against conversation text
            for field_name, field_config in fields.items():
                extraction_patterns = field_config.get('extraction_patterns', [])
                found = False

                for pattern in extraction_patterns:
                    if pattern.lower() in conversation_text.lower():
                        required_fields.append(field_name)
                        found = True
                        break

                if not found and field_config.get('required', False):
                    missing_fields.append(field_name)

            prompt = f"""
            Extract the requirements for creating a {document_type} from this conversation.

            Conversation:
            {conversation_text}

            For a {document_type}, identify:
            1. Required fields (names, addresses, dates, amounts, etc.)
            2. Key information mentioned
            3. Specific requirements or preferences

            Respond with JSON:
            {{
                "required_fields": ["field1", "field2"],
                "extracted_info": {{
                    "field1": "value1",
                    "field2": "value2"
                }},
                "missing_fields": ["field3", "field4"],
                "preferences": ["preference1", "preference2"]
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
                    result = {
                        'required_fields': required_fields,
                        'extracted_info': extracted_info,
                        'missing_fields': missing_fields,
                        'preferences': []
                    }

            return result

        except Exception as e:
            print(f"Error extracting requirements: {str(e)}")
            return {
                'required_fields': [],
                'extracted_info': {},
                'missing_fields': [],
                'preferences': []
            }

    def _extract_key_information(self, conversation_text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract key information from conversation for document generation
        """
        try:
            prompt = f"""
            Extract key information from this conversation that would be needed for a {document_type}.

            Conversation:
            {conversation_text}

            Extract:
            1. Names (people, companies, organizations)
            2. Addresses
            3. Dates
            4. Amounts (money, quantities)
            5. Key facts or events
            6. Legal basis or reasons

            Respond with JSON:
            {{
                "names": ["name1", "name2"],
                "addresses": ["address1", "address2"],
                "dates": ["date1", "date2"],
                "amounts": ["amount1", "amount2"],
                "facts": ["fact1", "fact2"],
                "legal_basis": ["basis1", "basis2"]
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
                    result = {
                        'names': [],
                        'addresses': [],
                        'dates': [],
                        'amounts': [],
                        'facts': [],
                        'legal_basis': []
                    }

            return result

        except Exception as e:
            print(f"Error extracting key information: {str(e)}")
            return {
                'names': [],
                'addresses': [],
                'dates': [],
                'amounts': [],
                'facts': [],
                'legal_basis': []
            }