"""
Dynamic Schema Loader
Handles any document type without hardcoding specific schemas
"""

import yaml
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class DynamicSchemaLoader:
    """
    Loads and manages document schemas dynamically
    Can handle any document type without hardcoding
    """
    
    def __init__(self, schemas_dir: str = None):
        self.schemas_dir = schemas_dir or os.path.join(os.path.dirname(__file__), 'schemas')
        self.schemas = {}
        self.load_all_schemas()
    
    def load_all_schemas(self):
        """Load all schema files from the schemas directory"""
        if not os.path.exists(self.schemas_dir):
            os.makedirs(self.schemas_dir, exist_ok=True)
            return
        
        for file_path in Path(self.schemas_dir).glob('*.yaml'):
            schema_name = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    schema_data = yaml.safe_load(f)
                    self.schemas[schema_name] = schema_data
            except Exception as e:
                print(f"Error loading schema {schema_name}: {e}")
    
    def get_schema(self, document_type: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific document type"""
        return self.schemas.get(document_type)
    
    def list_available_schemas(self) -> List[str]:
        """List all available document schemas"""
        return list(self.schemas.keys())
    
    def create_dynamic_schema(self, document_type: str, conversation_context: str) -> Dict[str, Any]:
        """
        Create a dynamic schema based on conversation context
        This is the core method that makes the system flexible
        """
        
        # Extract document characteristics from conversation
        characteristics = self._analyze_conversation_context(conversation_context)
        
        # Generate dynamic schema
        schema = {
            'name': characteristics.get('name', document_type.replace('_', ' ').title()),
            'description': characteristics.get('description', f'Dynamic {document_type} document'),
            'category': characteristics.get('category', 'general'),
            'jurisdiction': characteristics.get('jurisdiction', 'kenya'),
            
            # Dynamic field discovery
            'field_discovery': self._generate_field_discovery(characteristics),
            
            # Dynamic field generation
            'field_generation': self._generate_field_generation_rules(characteristics),
            
            # Validation rules
            'validation': self._generate_validation_rules(characteristics),
            
            # Document templates
            'templates': self._generate_templates(characteristics),
            
            # Review workflow
            'review_workflow': self._generate_review_workflow(characteristics),
            
            # User interaction
            'user_interaction': self._generate_user_interaction(characteristics)
        }
        
        return schema
    
    def _analyze_conversation_context(self, conversation: str) -> Dict[str, Any]:
        """
        Analyze conversation to determine document characteristics
        This is where the AI determines what type of document is needed
        """
        conversation_lower = conversation.lower()
        
        characteristics = {
            'name': 'Dynamic Document',
            'description': 'Generated based on conversation context',
            'category': 'general',
            'jurisdiction': 'kenya',
            'parties_involved': [],
            'key_topics': [],
            'legal_requirements': [],
            'business_terms': []
        }
        
        # Detect document type based on keywords
        if any(word in conversation_lower for word in ['employment', 'employee', 'employer', 'job', 'work']):
            characteristics.update({
                'name': 'Employment Contract',
                'category': 'employment',
                'parties_involved': ['employer', 'employee'],
                'key_topics': ['salary', 'working hours', 'benefits', 'termination']
            })
        
        elif any(word in conversation_lower for word in ['lease', 'rent', 'tenant', 'landlord', 'property']):
            characteristics.update({
                'name': 'Lease Agreement',
                'category': 'property',
                'parties_involved': ['landlord', 'tenant'],
                'key_topics': ['rent', 'duration', 'property details', 'utilities']
            })
        
        elif any(word in conversation_lower for word in ['partnership', 'business', 'company', 'venture']):
            characteristics.update({
                'name': 'Partnership Agreement',
                'category': 'business',
                'parties_involved': ['partner1', 'partner2'],
                'key_topics': ['capital', 'profit sharing', 'management', 'dissolution']
            })
        
        elif any(word in conversation_lower for word in ['service', 'consulting', 'freelance', 'contractor']):
            characteristics.update({
                'name': 'Service Agreement',
                'category': 'services',
                'parties_involved': ['client', 'service_provider'],
                'key_topics': ['scope', 'payment', 'deliverables', 'timeline']
            })
        
        # Extract specific details
        characteristics['legal_requirements'] = self._extract_legal_requirements(conversation_lower)
        characteristics['business_terms'] = self._extract_business_terms(conversation_lower)
        
        return characteristics
    
    def _extract_legal_requirements(self, conversation: str) -> List[str]:
        """Extract legal requirements from conversation"""
        requirements = []
        
        if 'confidentiality' in conversation or 'nda' in conversation:
            requirements.append('confidentiality_clause')
        
        if 'non-compete' in conversation or 'restrictive' in conversation:
            requirements.append('non_compete_clause')
        
        if 'termination' in conversation or 'notice' in conversation:
            requirements.append('termination_procedures')
        
        if 'dispute' in conversation or 'arbitration' in conversation:
            requirements.append('dispute_resolution')
        
        return requirements
    
    def _extract_business_terms(self, conversation: str) -> List[str]:
        """Extract business terms from conversation"""
        terms = []
        
        # Financial terms
        if any(word in conversation for word in ['salary', 'payment', 'compensation', 'fee']):
            terms.append('financial_terms')
        
        # Duration terms
        if any(word in conversation for word in ['duration', 'period', 'term', 'length']):
            terms.append('duration_terms')
        
        # Performance terms
        if any(word in conversation for word in ['performance', 'evaluation', 'review']):
            terms.append('performance_terms')
        
        return terms
    
    def _generate_field_discovery(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate field discovery patterns based on characteristics"""
        field_discovery = {}
        
        # Generate party fields
        if characteristics.get('parties_involved'):
            field_discovery['parties'] = []
            for party in characteristics['parties_involved']:
                field_discovery['parties'].append({
                    'pattern': f"{party}|{party.replace('_', ' ')}",
                    'field_type': 'party',
                    'role': party,
                    'priority': 'critical'
                })
        
        # Generate topic-based fields
        for topic in characteristics.get('key_topics', []):
            field_discovery[topic] = []
            if topic == 'salary':
                field_discovery[topic].append({
                    'pattern': 'salary|compensation|payment|remuneration',
                    'field_type': 'currency',
                    'validation': 'required',
                    'priority': 'high'
                })
            elif topic == 'duration':
                field_discovery[topic].append({
                    'pattern': 'duration|period|term|length',
                    'field_type': 'duration',
                    'validation': 'required',
                    'priority': 'high'
                })
        
        return field_discovery
    
    def _generate_field_generation_rules(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate field generation rules"""
        return {
            'auto_fields': [
                {
                    'trigger': 'parties_mentioned',
                    'generate': [f"{party}_details" for party in characteristics.get('parties_involved', [])]
                }
            ],
            'conditional_fields': [
                {
                    'condition': 'confidentiality_required',
                    'add_fields': ['confidentiality_scope', 'duration', 'penalties']
                }
            ]
        }
    
    def _generate_validation_rules(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation rules"""
        return {
            'required_sections': characteristics.get('key_topics', []),
            'legal_requirements': characteristics.get('legal_requirements', []),
            'business_logic': [
                'start_date <= end_date',
                'amount >= 0'
            ]
        }
    
    def _generate_templates(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate document templates"""
        return {
            'standard': {
                'name': f"Standard {characteristics['name']}",
                'sections': characteristics.get('key_topics', [])
            }
        }
    
    def _generate_review_workflow(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate review workflow"""
        return {
            'stages': [
                {
                    'name': 'Information Gathering',
                    'description': 'Extract and validate all required information',
                    'validation': 'required_fields_complete'
                },
                {
                    'name': 'Legal Compliance',
                    'description': 'Ensure compliance with relevant laws',
                    'validation': 'legal_requirements_met'
                },
                {
                    'name': 'Business Terms',
                    'description': 'Review and finalize business terms',
                    'validation': 'business_terms_agreed'
                },
                {
                    'name': 'Document Generation',
                    'description': 'Generate final document',
                    'validation': 'document_complete'
                }
            ]
        }
    
    def _generate_user_interaction(self, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user interaction patterns"""
        return {
            'information_gathering': [
                f"What are the details for {party}?" for party in characteristics.get('parties_involved', [])
            ] + [
                f"What are the {topic}?" for topic in characteristics.get('key_topics', [])
            ],
            'validation_questions': [
                "Please confirm all party details",
                "Please review the key terms",
                "Please confirm legal compliance"
            ],
            'final_confirmation': [
                "All information has been reviewed and is correct",
                "The document complies with relevant laws",
                "All parties agree to the terms",
                "Ready to generate final document"
            ]
        }
    
    def save_schema(self, document_type: str, schema: Dict[str, Any]):
        """Save a schema to file for future use"""
        schema_file = os.path.join(self.schemas_dir, f"{document_type}.yaml")
        with open(schema_file, 'w', encoding='utf-8') as f:
            yaml.dump(schema, f, default_flow_style=False, indent=2)
        
        # Reload schemas
        self.load_all_schemas() 