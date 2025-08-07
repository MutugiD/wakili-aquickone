import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.agent.drafting_agent.drafting_agent import DraftingAgent
from backend.agent.conversation_analyzer import ConversationAnalyzer
from backend.entity_mapper.entity_mapper import EntityMapper

# In-memory storage for drafts (in production, use database)
DRAFT_STORAGE: Dict[str, Dict[str, Any]] = {}

class DraftVersion:
    def __init__(self, version_id: str, content: Dict[str, Any], created_by: str):
        self.id = version_id
        self.content = content
        self.created_by = created_by
        self.created_at = datetime.now()
        self.status = 'pending'  # pending, approved, rejected, modified
        self.user_feedback = None
        self.approved_by = None
        self.approved_at = None
        self.rejected_reason = None
        self.modifications = {}
        self.metadata = {
            'sources': [],
            'confidence': 0.0,
            'generation_time': datetime.now().isoformat(),
            'template_used': None,
            'customizations': []
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat(),
            'status': self.status,
            'userFeedback': self.user_feedback,
            'approvedBy': self.approved_by,
            'approvedAt': self.approved_at.isoformat() if self.approved_at else None,
            'rejectedReason': self.rejected_reason,
            'modifications': self.modifications,
            'metadata': self.metadata
        }

class DocumentDraft:
    def __init__(self, draft_id: str, user_id: str, chat_id: str, document_type: str):
        self.id = draft_id
        self.user_id = user_id
        self.chat_id = chat_id
        self.document_type = document_type
        self.title = f"{document_type.replace('_', ' ').title()} Draft"
        self.status = 'in_progress'  # in_progress, completed, archived
        self.current_version = 1
        self.versions: List[DraftVersion] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.estimated_completion = None
        self.workflow_id = None
        self.settings = {
            'auto_approve': True,
            'require_user_approval': False,
            'max_versions': 10,
            'allow_modifications': True
        }

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'userId': self.user_id,
            'chatId': self.chat_id,
            'documentType': self.document_type,
            'title': self.title,
            'status': self.status,
            'currentVersion': self.current_version,
            'totalVersions': len(self.versions),
            'versions': [version.to_dict() for version in self.versions],
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'estimatedCompletion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'workflowId': self.workflow_id,
            'settings': self.settings
        }

        # Include original_content if it exists (for content-based drafts)
        if hasattr(self, 'original_content') and self.original_content:
            result['originalContent'] = self.original_content

        return result

class DraftingService:
    def __init__(self):
        self.drafting_agent = DraftingAgent()
        self.conversation_analyzer = ConversationAnalyzer()
        self.entity_mapper = EntityMapper()

    def create_draft_from_chat(self, user_id: str, chat_id: str, document_type: str = None) -> DocumentDraft:
        """Create a new document draft from an existing chat"""
        draft_id = str(uuid4())

        # Analyze chat to determine document type if not provided
        if not document_type:
            try:
                chat_messages = self._load_chat_messages(user_id, chat_id)

                # Check if we have any messages
                if not chat_messages:
                    logging.warning(f"No chat messages found for user {user_id}, chat {chat_id}")
                    document_type = 'custom_document'
                else:
                    analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)
                    document_type = analysis_result.get('document_type', 'custom_document')

            except Exception as e:
                logging.error(f"Error analyzing chat for document type: {str(e)}")
                document_type = 'custom_document'

        # Create draft
        draft = DocumentDraft(draft_id, user_id, chat_id, document_type)

        # Store draft
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return draft

    def create_draft_from_content(self, user_id: str, chat_content: str, document_type: str = None) -> DocumentDraft:
        """Create a new document draft from raw chat content"""
        draft_id = str(uuid4())

        # Analyze content to determine document type if not provided
        if not document_type:
            try:
                # Parse the chat content into a structured format
                chat_messages = self._parse_chat_content(chat_content)

                if not chat_messages:
                    logging.warning(f"No valid chat messages found in content for user {user_id}")
                    document_type = 'custom_document'
                else:
                    analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)
                    document_type = analysis_result.get('document_type', 'custom_document')

            except Exception as e:
                logging.error(f"Error analyzing chat content for document type: {str(e)}")
                document_type = 'custom_document'

        # Create draft with a placeholder chat_id for content-based drafts
        chat_id = f"content_{draft_id}"
        draft = DocumentDraft(draft_id, user_id, chat_id, document_type)

        # Store the original content for later use
        draft.original_content = chat_content

        # Store draft
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return draft

    def _parse_chat_content(self, chat_content: str) -> List[Dict[str, Any]]:
        """Parse raw chat content into structured message format"""
        messages = []
        lines = chat_content.strip().split('\n')

        current_role = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with role indicators
            if line.lower().startswith(('user:', 'human:', 'client:')):
                # Save previous message if exists
                if current_role and current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content).strip()
                    })

                current_role = 'user'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']

            elif line.lower().startswith(('assistant:', 'ai:', 'bot:', 'wakili:')):
                # Save previous message if exists
                if current_role and current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content).strip()
                    })

                current_role = 'assistant'
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']

            else:
                # Continue current message
                if current_role:
                    current_content.append(line)

        # Add the last message
        if current_role and current_content:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_content).strip()
            })

        return messages

    def get_user_drafts(self, user_id: str) -> List[DocumentDraft]:
        """Get all drafts for a user"""
        drafts = []
        for draft_data in DRAFT_STORAGE.values():
            if draft_data.get('userId') == user_id:
                draft = self._dict_to_draft(draft_data)
                drafts.append(draft)
        return drafts

    def get_draft(self, draft_id: str) -> Optional[DocumentDraft]:
        """Get a specific draft by ID"""
        if draft_id in DRAFT_STORAGE:
            return self._dict_to_draft(DRAFT_STORAGE[draft_id])
        return None

    async def generate_draft_version(self, draft_id: str, user_id: str, context: Dict[str, Any] = None) -> Optional[DraftVersion]:
        """Generate a new version of a document draft"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return None

        # Load chat context - handle both chat-based and content-based drafts
        if hasattr(draft, 'original_content') and draft.original_content:
            # Content-based draft
            chat_messages = self._parse_chat_content(draft.original_content)
        else:
            # Chat-based draft
            chat_messages = self._load_chat_messages(user_id, draft.chat_id)

        # Generate draft content using drafting agent
        draft_content = await self._generate_draft_content(chat_messages, draft.document_type, context)

        # Create new version
        version_id = str(uuid4())
        version = DraftVersion(version_id, draft_content, user_id)

        # Add to draft
        draft.versions.append(version)
        draft.current_version = len(draft.versions)
        draft.updated_at = datetime.now()

        # Update storage
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return version

    async def approve_draft_version(self, draft_id: str, version_id: str, user_id: str, feedback: str = None) -> bool:
        """Approve a draft version"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return False

        version = next((v for v in draft.versions if v.id == version_id), None)
        if not version or version.status != 'pending':
            return False

        # Approve version
        version.status = 'approved'
        version.approved_by = user_id
        version.approved_at = datetime.now()
        version.user_feedback = feedback

        # Update draft status
        draft.status = 'completed'
        draft.updated_at = datetime.now()

        # Update storage
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return True

    async def reject_draft_version(self, draft_id: str, version_id: str, user_id: str, reason: str, feedback: str = None) -> bool:
        """Reject a draft version with feedback"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return False

        version = next((v for v in draft.versions if v.id == version_id), None)
        if not version or version.status != 'pending':
            return False

        # Reject version
        version.status = 'rejected'
        version.rejected_reason = reason
        version.user_feedback = feedback

        # Update draft status
        draft.status = 'in_progress'
        draft.updated_at = datetime.now()

        # Update storage
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return True

    async def modify_draft_version(self, draft_id: str, version_id: str, user_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify a draft version with user input"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return False

        version = next((v for v in draft.versions if v.id == version_id), None)
        if not version:
            return False

        # Apply modifications
        version.modifications.update(modifications)
        version.status = 'modified'
        version.user_feedback = modifications.get('feedback', '')

        # Update draft
        draft.updated_at = datetime.now()
        DRAFT_STORAGE[draft_id] = draft.to_dict()

        return True

    async def regenerate_draft_version(self, draft_id: str, version_id: str, user_id: str, feedback: str = None) -> Optional[DraftVersion]:
        """Regenerate a draft version based on user feedback"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return None

        # Load chat context and previous feedback
        chat_messages = self._load_chat_messages(user_id, draft.chat_id)

        # Get previous version for context
        previous_version = next((v for v in draft.versions if v.id == version_id), None)

        # Generate new version with feedback
        context = {
            'previous_version': previous_version.content if previous_version else None,
            'user_feedback': feedback,
            'rejection_reason': previous_version.rejected_reason if previous_version else None,
            'modifications': previous_version.modifications if previous_version else {}
        }

        return await self.generate_draft_version(draft_id, user_id, context)

    def get_draft_comparison(self, draft_id: str, version_id_1: str, version_id_2: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Compare two versions of a draft"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return None

        version_1 = next((v for v in draft.versions if v.id == version_id_1), None)
        version_2 = next((v for v in draft.versions if v.id == version_id_2), None)

        if not version_1 or not version_2:
            return None

        # Compare versions
        comparison = self._compare_versions(version_1, version_2)

        return {
            'version1': version_1.to_dict(),
            'version2': version_2.to_dict(),
            'comparison': comparison
        }

    def export_draft(self, draft_id: str, user_id: str, format: str = 'json') -> Optional[Union[bytes, str]]:
        """Export a draft in specified format"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return None

        # Get latest approved version or current version
        latest_version = None
        for version in reversed(draft.versions):
            if version.status == 'approved':
                latest_version = version
                break

        if not latest_version:
            latest_version = draft.versions[-1] if draft.versions else None

        if not latest_version:
            return None

        # Prepare export data
        export_data = {
            'draft': {
                'id': draft.id,
                'title': draft.title,
                'documentType': draft.document_type,
                'status': draft.status,
                'createdAt': draft.created_at.isoformat(),
                'updatedAt': draft.updated_at.isoformat()
            },
            'version': latest_version.to_dict(),
            'exportedAt': datetime.now().isoformat()
        }

        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'txt':
            return self._export_as_text(latest_version.content)
        elif format == 'docx':
            # TODO: Implement DOCX export
            return json.dumps(export_data, indent=2)
        elif format == 'pdf':
            # TODO: Implement PDF export
            return json.dumps(export_data, indent=2)

        return None

    def delete_draft(self, draft_id: str, user_id: str) -> bool:
        """Delete a draft"""
        draft = self.get_draft(draft_id)
        if not draft or draft.user_id != user_id:
            return False

        if draft_id in DRAFT_STORAGE:
            del DRAFT_STORAGE[draft_id]
            return True

        return False

    async def _generate_draft_content(self, chat_messages: List[Dict[str, Any]], document_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate draft content using the drafting agent"""
        try:
            # Extract conversation text
            conversation_text = self._extract_conversation_text(chat_messages)

            # Analyze conversation for document requirements
            analysis_result = self.conversation_analyzer.analyze_conversation(chat_messages)

            # Prepare context for drafting
            drafting_context = {
                'conversation_text': conversation_text,
                'document_type': document_type,
                'analysis_result': analysis_result,
                'user_context': context or {}
            }

            # Generate draft using drafting agent
            draft_result = self.drafting_agent.draft_document(document_type, drafting_context)

            return {
                'document_type': document_type,
                'content': draft_result,
                'sections': [{'title': document_type.replace('_', ' ').title(), 'content': draft_result}],
                'metadata': {
                    'generation_time': datetime.now().isoformat(),
                    'confidence': 0.8,
                    'sources': [],
                    'template_used': document_type,
                    'customizations': []
                }
            }

        except Exception as e:
            logging.error(f"Error generating draft content: {str(e)}")
            return {
                'document_type': document_type,
                'content': {'error': str(e)},
                'sections': [],
                'metadata': {
                    'generation_time': datetime.now().isoformat(),
                    'confidence': 0.0,
                    'sources': [],
                    'template_used': '',
                    'customizations': []
                }
            }

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
                        # Ensure content is not None before processing
                        content = msg.content if msg.content is not None else ""
                        chat_messages.append({
                            'role': msg.type,
                            'content': content
                        })
                return chat_messages
        except Exception as e:
            logging.error(f"Error loading chat messages: {str(e)}")

        return []

    def _extract_conversation_text(self, chat_messages: List[Dict[str, Any]]) -> str:
        """Extract conversation text from messages"""
        return "\n".join([msg.get('content', '') for msg in chat_messages])

    def _compare_versions(self, version_1: DraftVersion, version_2: DraftVersion) -> Dict[str, Any]:
        """Compare two draft versions"""
        # Simple comparison - in production, use more sophisticated diffing
        return {
            'content_changes': self._diff_content(version_1.content, version_2.content),
            'metadata_changes': self._diff_metadata(version_1.metadata, version_2.metadata),
            'status_changes': {
                'from': version_1.status,
                'to': version_2.status
            }
        }

    def _diff_content(self, content_1: Dict[str, Any], content_2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simple content diffing"""
        changes = []
        # TODO: Implement proper diffing algorithm
        return changes

    def _diff_metadata(self, metadata_1: Dict[str, Any], metadata_2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simple metadata diffing"""
        changes = []
        # TODO: Implement proper diffing algorithm
        return changes

    def _export_as_text(self, content: Dict[str, Any]) -> str:
        """Export draft content as plain text"""
        if not content:
            return "No content available"

        # Convert content to text format
        text_parts = []

        # Handle different content structures
        if isinstance(content, dict):
            if 'sections' in content and isinstance(content['sections'], list):
                for section in content['sections']:
                    if isinstance(section, dict):
                        if 'title' in section:
                            text_parts.append(f"\n{section['title']}\n")
                        if 'content' in section:
                            text_parts.append(str(section['content']))

            if 'content' in content:
                if isinstance(content['content'], str):
                    text_parts.append(content['content'])
                elif isinstance(content['content'], dict):
                    text_parts.append(json.dumps(content['content'], indent=2))

            # Add any other text fields
            for key, value in content.items():
                if key not in ['sections', 'content'] and isinstance(value, str):
                    text_parts.append(f"{key}: {value}")

        elif isinstance(content, str):
            text_parts.append(content)

        result = "\n".join(text_parts)
        return result if result.strip() else "Content exported successfully"

    def _dict_to_draft(self, draft_data: Dict[str, Any]) -> DocumentDraft:
        """Convert dictionary back to DocumentDraft object"""
        draft = DocumentDraft(
            draft_data['id'],
            draft_data['userId'],
            draft_data['chatId'],
            draft_data['documentType']
        )
        draft.title = draft_data['title']
        draft.status = draft_data['status']
        draft.current_version = draft_data['currentVersion']
        draft.created_at = datetime.fromisoformat(draft_data['createdAt'])
        draft.updated_at = datetime.fromisoformat(draft_data['updatedAt'])
        draft.workflow_id = draft_data.get('workflowId')
        draft.settings = draft_data.get('settings', {})

        if draft_data.get('estimatedCompletion'):
            draft.estimated_completion = datetime.fromisoformat(draft_data['estimatedCompletion'])

        # Handle original_content for content-based drafts
        if 'originalContent' in draft_data:
            draft.original_content = draft_data['originalContent']

        # Convert versions
        draft.versions = []
        for version_data in draft_data['versions']:
            version = DraftVersion(
                version_data['id'],
                version_data['content'],
                version_data['createdBy']
            )
            version.created_at = datetime.fromisoformat(version_data['createdAt'])
            version.status = version_data['status']
            version.user_feedback = version_data.get('userFeedback')
            version.approved_by = version_data.get('approvedBy')
            version.rejected_reason = version_data.get('rejectedReason')
            version.modifications = version_data.get('modifications', {})
            version.metadata = version_data.get('metadata', {})

            if version_data.get('approvedAt'):
                version.approved_at = datetime.fromisoformat(version_data['approvedAt'])

            draft.versions.append(version)

        return draft