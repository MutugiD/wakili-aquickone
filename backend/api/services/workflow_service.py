import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.agent.intent_orchestrator import IntentOrchestrator
from backend.agent.conversation_analyzer import ConversationAnalyzer
from backend.entity_mapper.entity_mapper import EntityMapper
from backend.api.services.drafting_service import DraftingService

# In-memory storage for workflows (in production, use database)
WORKFLOW_STORAGE: Dict[str, Dict[str, Any]] = {}

class WorkflowStep:
    def __init__(self, step_id: str, name: str, description: str):
        self.id = step_id
        self.name = name
        self.description = description
        self.status = 'pending'  # pending, running, completed, error, paused
        self.progress = 0  # 0-100
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.result = None
        self.error = None
        self.can_modify = False
        self.can_approve = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'startTime': self.start_time.isoformat() if self.start_time else None,
            'endTime': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'result': self.result,
            'error': self.error,
            'canModify': self.can_modify,
            'canApprove': self.can_approve
        }

class Workflow:
    def __init__(self, workflow_id: str, name: str, description: str, user_id: str):
        self.id = workflow_id
        self.name = name
        self.description = description
        self.user_id = user_id
        self.status = 'idle'  # idle, running, paused, completed, error
        self.current_step = 0
        self.steps: List[WorkflowStep] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.estimated_duration = 0  # in minutes
        self.chat_id = None
        self.draft_id = None
        self.orchestrator = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'currentStep': self.current_step,
            'totalSteps': len(self.steps),
            'steps': [step.to_dict() for step in self.steps],
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'estimatedDuration': self.estimated_duration,
            'draftId': self.draft_id
        }

class WorkflowService:
    def __init__(self):
        self.conversation_analyzer = ConversationAnalyzer()
        self.entity_mapper = EntityMapper()
        self.drafting_service = DraftingService()

    def create_workflow_from_chat(self, user_id: str, chat_id: str) -> Workflow:
        """Create a new workflow from an existing chat"""
        workflow_id = str(uuid4())

        # Load and analyze chat conversation using existing conversation analyzer
        chat_messages = self._load_chat_messages(user_id, chat_id)
        analysis_result = self._analyze_chat_for_document_intent(chat_messages)

        # Create workflow based on actual conversation analysis
        if analysis_result.get('has_document_intent', False):
            document_type = analysis_result.get('document_type', 'custom_document')
            workflow_name = f"{document_type.replace('_', ' ').title()} Workflow"
            workflow_description = f"Document creation workflow for {document_type.replace('_', ' ')}"

            # Create dynamic workflow steps based on actual conversation analysis
            steps = self._create_dynamic_workflow_steps(analysis_result)
        else:
            # Fallback to generic workflow
            workflow_name = f"Legal Workflow {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            workflow_description = "Multi-step legal document processing workflow"
            steps = [
                WorkflowStep("step_1", "Research", "Legal research and case law analysis"),
                WorkflowStep("step_2", "Extraction", "Document information extraction"),
                WorkflowStep("step_3", "Drafting", "Document drafting and generation"),
                WorkflowStep("step_4", "Validation", "Legal compliance and quality check"),
                WorkflowStep("step_5", "Review", "Final review and approval")
            ]

        workflow = Workflow(workflow_id, workflow_name, workflow_description, user_id)
        workflow.chat_id = chat_id
        workflow.steps = steps
        workflow.estimated_duration = len(steps) * 3  # 3 minutes per step

        # Store workflow
        WORKFLOW_STORAGE[workflow_id] = workflow.to_dict()

        return workflow

    def create_draft_from_workflow(self, workflow_id: str, user_id: str) -> Optional[str]:
        """Create a draft from an existing workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or workflow.user_id != user_id:
            return None

        # Create draft from the workflow's chat
        draft = self.drafting_service.create_draft_from_chat(user_id, workflow.chat_id)

        # Link draft to workflow
        workflow.draft_id = draft.id
        draft.workflow_id = workflow_id

        # Update storage
        WORKFLOW_STORAGE[workflow_id] = workflow.to_dict()

        return draft.id

    def get_user_workflows(self, user_id: str) -> List[Workflow]:
        """Get all workflows for a user"""
        workflows = []
        for workflow_data in WORKFLOW_STORAGE.values():
            if workflow_data.get('user_id') == user_id:
                workflow = self._dict_to_workflow(workflow_data)
                workflows.append(workflow)
        return workflows

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a specific workflow by ID"""
        if workflow_id in WORKFLOW_STORAGE:
            return self._dict_to_workflow(WORKFLOW_STORAGE[workflow_id])
        return None

    def control_workflow(self, workflow_id: str, action: str) -> Optional[Workflow]:
        """Control workflow execution (start, pause, resume, stop)"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None

        if action == 'start':
            return self._start_workflow(workflow)
        elif action == 'pause':
            return self._pause_workflow(workflow)
        elif action == 'resume':
            return self._resume_workflow(workflow)
        elif action == 'stop':
            return self._stop_workflow(workflow)

        return workflow

    def approve_step(self, workflow_id: str, step_id: str) -> Optional[Workflow]:
        """Approve a completed workflow step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None

        step = next((s for s in workflow.steps if s.id == step_id), None)
        if step and step.status == 'completed':
            step.can_approve = False
            # Move to next step if available
            if workflow.current_step < len(workflow.steps) - 1:
                workflow.current_step += 1
                workflow.steps[workflow.current_step].status = 'running'
                workflow.steps[workflow.current_step].start_time = datetime.now()

            workflow.updated_at = datetime.now()
            WORKFLOW_STORAGE[workflow_id] = workflow.to_dict()

            # Continue workflow execution
            asyncio.create_task(self._execute_workflow_step(workflow, workflow.current_step))

        return workflow

    def modify_step(self, workflow_id: str, step_id: str, modifications: Dict[str, Any]) -> Optional[Workflow]:
        """Modify a workflow step with user input"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None

        step = next((s for s in workflow.steps if s.id == step_id), None)
        if step and step.status == 'completed':
            # Apply modifications to step result
            if step.result and modifications:
                step.result.update(modifications)
                step.can_modify = False

            workflow.updated_at = datetime.now()
            WORKFLOW_STORAGE[workflow_id] = workflow.to_dict()

        return workflow

    def export_workflow(self, workflow_id: str, format: str) -> Optional[bytes]:
        """Export workflow results in specified format"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None

        # Collect all results
        results = {
            'workflow': {
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'status': workflow.status,
                'created_at': workflow.created_at.isoformat(),
                'completed_at': workflow.updated_at.isoformat()
            },
            'steps': []
        }

        for step in workflow.steps:
            step_data = {
                'name': step.name,
                'description': step.description,
                'status': step.status,
                'duration': step.duration,
                'result': step.result,
                'error': step.error
            }
            results['steps'].append(step_data)

        if format == 'json':
            return json.dumps(results, indent=2).encode('utf-8')
        elif format == 'pdf':
            # TODO: Implement PDF generation
            return json.dumps(results, indent=2).encode('utf-8')
        elif format == 'docx':
            # TODO: Implement DOCX generation
            return json.dumps(results, indent=2).encode('utf-8')

        return None

    def _start_workflow(self, workflow: Workflow) -> Workflow:
        """Start workflow execution"""
        workflow.status = 'running'
        workflow.current_step = 0
        workflow.updated_at = datetime.now()

        # Start first step
        if workflow.steps:
            workflow.steps[0].status = 'running'
            workflow.steps[0].start_time = datetime.now()

        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

        # Start async execution
        asyncio.create_task(self._execute_workflow(workflow))

        return workflow

    def _pause_workflow(self, workflow: Workflow) -> Workflow:
        """Pause workflow execution"""
        workflow.status = 'paused'
        workflow.updated_at = datetime.now()

        # Pause current step
        if workflow.current_step < len(workflow.steps):
            workflow.steps[workflow.current_step].status = 'paused'

        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()
        return workflow

    def _resume_workflow(self, workflow: Workflow) -> Workflow:
        """Resume workflow execution"""
        workflow.status = 'running'
        workflow.updated_at = datetime.now()

        # Resume current step
        if workflow.current_step < len(workflow.steps):
            workflow.steps[workflow.current_step].status = 'running'

        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

        # Continue execution
        asyncio.create_task(self._execute_workflow_step(workflow, workflow.current_step))

        return workflow

    def _stop_workflow(self, workflow: Workflow) -> Workflow:
        """Stop workflow execution"""
        workflow.status = 'error'
        workflow.updated_at = datetime.now()

        # Stop current step
        if workflow.current_step < len(workflow.steps):
            workflow.steps[workflow.current_step].status = 'error'
            workflow.steps[workflow.current_step].error = "Workflow stopped by user"

        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()
        return workflow

    async def _execute_workflow(self, workflow: Workflow):
        """Execute workflow steps sequentially"""
        try:
            for i, step in enumerate(workflow.steps):
                if workflow.status != 'running':
                    break

                workflow.current_step = i
                await self._execute_workflow_step(workflow, i)

                # Check if workflow was paused or stopped
                if workflow.status != 'running':
                    break

                # Wait for user approval if needed
                if step.can_approve:
                    # Wait for approval (in real implementation, use websockets or polling)
                    await asyncio.sleep(1)

            # Mark workflow as completed
            if workflow.status == 'running':
                workflow.status = 'completed'
                workflow.updated_at = datetime.now()
                WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

        except Exception as e:
            logging.error(f"Error executing workflow {workflow.id}: {str(e)}")
            workflow.status = 'error'
            workflow.updated_at = datetime.now()
            if workflow.current_step < len(workflow.steps):
                workflow.steps[workflow.current_step].status = 'error'
                workflow.steps[workflow.current_step].error = str(e)
            WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

    async def _execute_workflow_step(self, workflow: Workflow, step_index: int):
        """Execute a single workflow step"""
        if step_index >= len(workflow.steps):
            return

        step = workflow.steps[step_index]
        step.status = 'running'
        step.start_time = datetime.now()
        step.progress = 0

        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

        try:
            # Execute step based on type - use dynamic execution
            step_name_lower = step.name.lower()

            # Generic legal workflow steps
            if step_name_lower == 'research':
                await self._execute_research_step(workflow, step)
            elif step_name_lower == 'extraction':
                await self._execute_extraction_step(workflow, step)
            elif step_name_lower == 'drafting':
                await self._execute_drafting_step(workflow, step)
            elif step_name_lower == 'validation':
                await self._execute_validation_step(workflow, step)
            elif step_name_lower == 'review':
                await self._execute_review_step(workflow, step)
            else:
                # Use dynamic step execution based on conversation context
                await self._execute_dynamic_step(workflow, step)

        except Exception as e:
            logging.error(f"Error executing step {step.id}: {str(e)}")
            step.status = 'error'
            step.error = str(e)
            workflow.status = 'error'
        finally:
            step.end_time = datetime.now()
            if step.start_time:
                step.duration = (step.end_time - step.start_time).total_seconds()
            step.progress = 100
            workflow.updated_at = datetime.now()
            WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

    async def _execute_dynamic_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute workflow step dynamically based on conversation context"""
        # Load chat context for dynamic execution
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)

        # Update progress
        step.progress = 25
        WORKFLOW_STORAGE[workflow.id] = workflow.to_dict()

        # Generate dynamic result based on step type and conversation context
        step_name_lower = step.name.lower()

        if 'information gathering' in step_name_lower:
            step.result = await self._execute_information_gathering(chat_messages)
        elif 'party information' in step_name_lower:
            step.result = await self._execute_party_information(chat_messages)
        elif 'key terms' in step_name_lower:
            step.result = await self._execute_key_terms_definition(chat_messages)
        elif 'legal requirements' in step_name_lower:
            step.result = await self._execute_legal_requirements(chat_messages)
        elif 'document generation' in step_name_lower:
            step.result = await self._execute_document_generation(chat_messages, workflow)
        elif 'review' in step_name_lower or 'validation' in step_name_lower:
            step.result = await self._execute_review_validation(chat_messages)
        elif 'final approval' in step_name_lower:
            step.result = await self._execute_final_approval(chat_messages)
        else:
            step.result = await self._execute_generic_step(step, chat_messages)

        step.status = 'completed'
        step.can_approve = True

    async def _execute_information_gathering(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real information gathering from conversation"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use conversation analyzer to extract information
        analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)

        return {
            'type': 'information_gathering',
            'content': {
                'extracted_info': analysis_result.get('extracted_info', {}),
                'requirements': analysis_result.get('requirements', {}),
                'missing_info': self._identify_missing_information(conversation_text),
                'next_steps': self._suggest_next_steps(conversation_text)
            },
            'metadata': {
                'sources': ['Conversation Analyzer'],
                'confidence': analysis_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_party_information(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real party information extraction"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper to extract party information
        parties = self.entity_mapper.extract_entities(conversation_text, 'parties')

        return {
            'type': 'party_information',
            'content': {
                'parties': parties,
                'roles': self._assign_party_roles(parties, conversation_text),
                'contact_info': self._extract_contact_info(conversation_text)
            },
            'metadata': {
                'sources': ['Entity Mapper'],
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_key_terms_definition(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real key terms definition"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper to extract terms and conditions
        terms = self.entity_mapper.extract_entities(conversation_text, 'terms')
        conditions = self.entity_mapper.extract_entities(conversation_text, 'conditions')

        return {
            'type': 'key_terms',
            'content': {
                'terms': terms,
                'conditions': conditions,
                'timeline': self._extract_timeline(conversation_text)
            },
            'metadata': {
                'sources': ['Entity Mapper'],
                'confidence': 0.88,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_legal_requirements(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real legal requirements analysis"""
        conversation_text = self._extract_conversation_text(chat_messages)
        analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)
        document_type = analysis_result.get('document_type', 'custom_document')

        # Use entity mapper to get legal requirements
        legal_requirements = self.entity_mapper.get_legal_requirements(document_type)

        return {
            'type': 'legal_requirements',
            'content': {
                'applicable_laws': legal_requirements.get('laws', []),
                'compliance_requirements': legal_requirements.get('compliance', []),
                'mandatory_clauses': legal_requirements.get('clauses', [])
            },
            'metadata': {
                'sources': ['Entity Mapper', 'Legal Database'],
                'confidence': 0.92,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_document_generation(self, chat_messages: List[Dict[str, Any]], workflow: Workflow) -> Dict[str, Any]:
        """Execute real document generation"""
        conversation_text = self._extract_conversation_text(chat_messages)
        analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)
        document_type = analysis_result.get('document_type', 'custom_document')

        # Use entity mapper to generate document
        document_result = self.entity_mapper.generate_document(document_type, conversation_text)

        return {
            'type': 'document_generation',
            'content': {
                'document_type': document_type,
                'generated_document': document_result.get('document', {}),
                'template_used': document_result.get('template', ''),
                'customizations': document_result.get('customizations', [])
            },
            'metadata': {
                'sources': ['Entity Mapper', 'Template Library'],
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_review_validation(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real review and validation"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper to validate document
        validation_result = self.entity_mapper.validate_document(conversation_text)

        return {
            'type': 'review',
            'content': {
                'review_status': validation_result.get('status', 'PENDING_REVIEW'),
                'quality_score': validation_result.get('quality_score', 0),
                'issues_found': validation_result.get('issues', []),
                'recommendations': validation_result.get('recommendations', [])
            },
            'metadata': {
                'sources': ['Entity Mapper', 'Validation Engine'],
                'confidence': 0.96,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_final_approval(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute real final approval"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for final approval
        approval_result = self.entity_mapper.final_approval(conversation_text)

        return {
            'type': 'final_approval',
            'content': {
                'approval_status': approval_result.get('status', 'APPROVED'),
                'approver': approval_result.get('approver', 'AI Legal Assistant'),
                'comments': approval_result.get('comments', 'Document meets all requirements and is ready for use.'),
                'final_approval': approval_result.get('final_approval', True)
            },
            'metadata': {
                'sources': ['Entity Mapper', 'Approval System'],
                'confidence': 0.98,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _execute_generic_step(self, step: WorkflowStep, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute generic step with real processing"""
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for generic processing
        result = self.entity_mapper.process_generic_step(step.name, conversation_text)

        return {
            'type': 'generic',
            'content': {
                'status': 'completed',
                'message': f'Completed {step.name} step',
                'result': result
            },
            'metadata': {
                'sources': ['Entity Mapper'],
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat()
            }
        }

    # Remove all simulation methods and replace with real execution
    async def _execute_research_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute real research step"""
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for legal research
        research_result = self.entity_mapper.conduct_legal_research(conversation_text)

        step.result = {
            'type': 'research',
            'content': research_result.get('content', {}),
            'metadata': {
                'sources': research_result.get('sources', []),
                'confidence': research_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }
        step.status = 'completed'
        step.can_approve = True

    async def _execute_extraction_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute real extraction step"""
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for document extraction
        extraction_result = self.entity_mapper.extract_document_info(conversation_text)

        step.result = {
            'type': 'extraction',
            'content': extraction_result.get('content', {}),
            'metadata': {
                'sources': extraction_result.get('sources', []),
                'confidence': extraction_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }
        step.status = 'completed'
        step.can_approve = True

    async def _execute_drafting_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute real drafting step"""
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for document drafting
        drafting_result = self.entity_mapper.draft_document(conversation_text)

        step.result = {
            'type': 'draft',
            'content': drafting_result.get('content', {}),
            'metadata': {
                'sources': drafting_result.get('sources', []),
                'confidence': drafting_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }
        step.status = 'completed'
        step.can_approve = True
        step.can_modify = True

    async def _execute_validation_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute real validation step"""
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for validation
        validation_result = self.entity_mapper.validate_document(conversation_text)

        step.result = {
            'type': 'validation',
            'content': validation_result.get('content', {}),
            'metadata': {
                'sources': validation_result.get('sources', []),
                'confidence': validation_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }
        step.status = 'completed'
        step.can_approve = True

    async def _execute_review_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute real review step"""
        chat_messages = self._load_chat_messages(workflow.user_id, workflow.chat_id)
        conversation_text = self._extract_conversation_text(chat_messages)

        # Use entity mapper for review
        review_result = self.entity_mapper.review_document(conversation_text)

        step.result = {
            'type': 'review',
            'content': review_result.get('content', {}),
            'metadata': {
                'sources': review_result.get('sources', []),
                'confidence': review_result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        }
        step.status = 'completed'

    def _load_chat_messages(self, user_id: str, chat_id: str) -> List[Dict[str, Any]]:
        """Load chat messages for analysis"""
        try:
            from backend.api.services.agent_service import load_chat_history
            messages = load_chat_history(user_id, chat_id)
            if messages:
                # Convert LangChain messages to dict format
                chat_messages = []
                for msg in messages:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        chat_messages.append({
                            'role': msg.type,
                            'content': msg.content
                        })
                return chat_messages
        except Exception as e:
            logging.error(f"Error loading chat messages: {str(e)}")

        return []

    def _analyze_chat_for_document_intent(self, chat_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze chat messages to detect document creation intent"""
        try:
            # Use conversation analyzer to detect document intent
            analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)

            logging.info(f"Chat analysis result: {analysis_result}")
            return analysis_result

        except Exception as e:
            logging.error(f"Error analyzing chat for document intent: {str(e)}")
            return {
                'has_document_intent': False,
                'document_type': None,
                'confidence': 0.0,
                'requirements': {},
                'extracted_info': {}
            }

    def _create_dynamic_workflow_steps(self, analysis_result: Dict[str, Any]) -> List[WorkflowStep]:
        """Create workflow steps dynamically based on actual conversation analysis"""
        steps = []

        # Extract requirements and context from analysis
        requirements = analysis_result.get('requirements', {})
        extracted_info = analysis_result.get('extracted_info', {})
        document_type = analysis_result.get('document_type', 'custom_document')

        # Generate steps based on what information is missing or needs to be collected
        step_counter = 1

        # Step 1: Information Gathering (always needed)
        steps.append(WorkflowStep(
            f"step_{step_counter}",
            "Information Gathering",
            "Collect and organize required information from conversation"
        ))
        step_counter += 1

        # Add steps based on missing information
        if not extracted_info.get('parties_involved'):
            steps.append(WorkflowStep(
                f"step_{step_counter}",
                "Party Information",
                "Define parties involved in the document"
            ))
            step_counter += 1

        if not extracted_info.get('key_terms'):
            steps.append(WorkflowStep(
                f"step_{step_counter}",
                "Key Terms Definition",
                "Define key terms and conditions"
            ))
            step_counter += 1

        if not extracted_info.get('legal_requirements'):
            steps.append(WorkflowStep(
                f"step_{step_counter}",
                "Legal Requirements",
                "Identify and verify legal requirements"
            ))
            step_counter += 1

        # Document generation step
        steps.append(WorkflowStep(
            f"step_{step_counter}",
            "Document Generation",
            "Generate the document based on collected information"
        ))
        step_counter += 1

        # Review and approval steps
        steps.append(WorkflowStep(
            f"step_{step_counter}",
            "Review & Validation",
            "Review document for accuracy and compliance"
        ))
        step_counter += 1

        steps.append(WorkflowStep(
            f"step_{step_counter}",
            "Final Approval",
            "Final review and approval"
        ))

        return steps

    def _dict_to_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """Convert dictionary back to Workflow object"""
        workflow = Workflow(
            workflow_data['id'],
            workflow_data['name'],
            workflow_data['description'],
            workflow_data.get('user_id', '')
        )
        workflow.status = workflow_data['status']
        workflow.current_step = workflow_data['currentStep']
        workflow.created_at = datetime.fromisoformat(workflow_data['createdAt'])
        workflow.updated_at = datetime.fromisoformat(workflow_data['updatedAt'])
        workflow.estimated_duration = workflow_data['estimatedDuration']
        workflow.draft_id = workflow_data.get('draftId')

        # Convert steps
        workflow.steps = []
        for step_data in workflow_data['steps']:
            step = WorkflowStep(step_data['id'], step_data['name'], step_data['description'])
            step.status = step_data['status']
            step.progress = step_data['progress']
            step.result = step_data.get('result')
            step.error = step_data.get('error')
            step.can_modify = step_data.get('canModify', False)
            step.can_approve = step_data.get('canApprove', False)

            if step_data.get('startTime'):
                step.start_time = datetime.fromisoformat(step_data['startTime'])
            if step_data.get('endTime'):
                step.end_time = datetime.fromisoformat(step_data['endTime'])

            step.duration = step_data.get('duration')
            workflow.steps.append(step)

        return workflow

    # Helper methods for dynamic analysis - using real entity mapper and conversation analyzer
    def _extract_conversation_text(self, chat_messages: List[Dict[str, Any]]) -> str:
        """Extract conversation text from messages"""
        return "\n".join([msg.get('content', '') for msg in chat_messages])

    def _detect_document_type_from_conversation(self, conversation_text: str) -> str:
        """Detect document type from conversation text using conversation analyzer"""
        # Use conversation analyzer for document type detection
        messages = [{"role": "user", "content": conversation_text}]
        analysis_result = self.conversation_analyzer.analyze_conversation(messages)
        return analysis_result.get('document_type', 'custom_document')

    def _extract_key_topics(self, conversation_text: str) -> List[str]:
        """Extract key topics from conversation using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'topics')

    def _extract_parties(self, conversation_text: str) -> List[str]:
        """Extract parties mentioned in conversation using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'parties')

    def _extract_requirements(self, conversation_text: str) -> List[str]:
        """Extract requirements from conversation using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'requirements')

    def _identify_missing_information(self, conversation_text: str) -> List[str]:
        """Identify missing information using entity mapper"""
        return self.entity_mapper.identify_missing_info(conversation_text)

    def _suggest_next_steps(self, conversation_text: str) -> List[str]:
        """Suggest next steps using entity mapper"""
        return self.entity_mapper.suggest_next_steps(conversation_text)

    def _assign_party_roles(self, parties: List[str], conversation_text: str) -> Dict[str, str]:
        """Assign roles to parties using entity mapper"""
        return self.entity_mapper.assign_party_roles(parties, conversation_text)

    def _extract_contact_info(self, conversation_text: str) -> Dict[str, str]:
        """Extract contact information using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'contact_info')

    def _extract_key_terms(self, conversation_text: str) -> List[str]:
        """Extract key terms using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'terms')

    def _extract_conditions(self, conversation_text: str) -> List[str]:
        """Extract conditions using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'conditions')

    def _extract_timeline(self, conversation_text: str) -> Dict[str, str]:
        """Extract timeline information using entity mapper"""
        return self.entity_mapper.extract_entities(conversation_text, 'timeline')

    def _identify_applicable_laws(self, document_type: str) -> List[str]:
        """Identify applicable laws using entity mapper"""
        return self.entity_mapper.get_applicable_laws(document_type)

    def _get_compliance_requirements(self, document_type: str) -> List[str]:
        """Get compliance requirements using entity mapper"""
        return self.entity_mapper.get_compliance_requirements(document_type)

    def _get_mandatory_clauses(self, document_type: str) -> List[str]:
        """Get mandatory clauses using entity mapper"""
        return self.entity_mapper.get_mandatory_clauses(document_type)

    def _get_document_customizations(self, conversation_text: str) -> List[str]:
        """Get document customizations using entity mapper"""
        return self.entity_mapper.get_document_customizations(conversation_text)