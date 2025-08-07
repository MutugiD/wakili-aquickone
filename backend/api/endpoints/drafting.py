from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import logging
import io

from backend.api.services.drafting_service import DraftingService
from backend.api.endpoints.auth import verify_supabase_jwt

router = APIRouter(prefix="/drafting", tags=["drafting"])

# Initialize drafting service
drafting_service = DraftingService()

@router.get("/")
async def get_drafts(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)) -> Dict[str, Any]:
    """Get all drafts for the authenticated user"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get user's drafts
        drafts = drafting_service.get_user_drafts(user_id)

        return {
            "success": True,
            "drafts": [draft.to_dict() for draft in drafts]
        }

    except Exception as e:
        logging.error(f"Error getting drafts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve drafts"
        )

@router.get("/{draft_id}")
async def get_draft(draft_id: str, user_data: Dict[str, Any] = Depends(verify_supabase_jwt)) -> Dict[str, Any]:
    """Get a specific draft by ID"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get draft
        draft = drafting_service.get_draft(draft_id)

        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )

        # Check if user owns this draft
        if draft.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return {
            "success": True,
            "draft": draft.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting draft {draft_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve draft"
        )

@router.post("/create-from-chat")
async def create_draft_from_chat(
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Create a new draft from an existing chat"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Extract request data
        chat_id = request.get("chat_id")
        chat_content = request.get("chat_content")
        document_type = request.get("document_type")

        # Validate that either chat_id or chat_content is provided
        if not chat_id and not chat_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either chat_id or chat_content is required"
            )

        # Validate chat_id format if provided
        if chat_id and (not isinstance(chat_id, str) or len(chat_id.strip()) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chat_id format"
            )

        # Validate chat_content format if provided
        if chat_content and (not isinstance(chat_content, str) or len(chat_content.strip()) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chat_content format"
            )

        # Create draft from chat or content
        try:
            if chat_id:
                draft = drafting_service.create_draft_from_chat(user_id, chat_id, document_type)
            else:
                draft = drafting_service.create_draft_from_content(user_id, chat_content, document_type)
        except Exception as e:
            logging.error(f"Error in drafting service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create draft: {str(e)}"
            )

        return {
            "success": True,
            "draft": draft.to_dict(),
            "message": "Draft created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating draft from chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create draft"
        )

@router.post("/{draft_id}/generate")
async def generate_draft_version(
    draft_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Generate a new version of a document draft"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get context from request
        context = request.get("context", {})

        # Generate draft version
        version = await drafting_service.generate_draft_version(draft_id, user_id, context)

        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or access denied"
            )

        # Get the updated draft with the new version
        updated_draft = drafting_service.get_draft(draft_id)

        if not updated_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found after generation"
            )

        return {
            "success": True,
            "draft": updated_draft.to_dict(),
            "version": version.to_dict(),
            "message": "Draft version generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate draft version"
        )

@router.post("/{draft_id}/versions/{version_id}/approve")
async def approve_draft_version(
    draft_id: str,
    version_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Approve a draft version"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get feedback from request
        feedback = request.get("feedback")

        # Approve draft version
        success = await drafting_service.approve_draft_version(draft_id, version_id, user_id, feedback)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft or version not found, or version cannot be approved"
            )

        # Get the updated draft
        updated_draft = drafting_service.get_draft(draft_id)

        if not updated_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found after approval"
            )

        return {
            "success": True,
            "draft": updated_draft.to_dict(),
            "message": "Draft version approved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error approving draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve draft version"
        )

@router.post("/{draft_id}/versions/{version_id}/reject")
async def reject_draft_version(
    draft_id: str,
    version_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Reject a draft version with feedback"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get feedback from request
        feedback = request.get("feedback")

        # Reject draft version
        success = await drafting_service.reject_draft_version(draft_id, version_id, user_id, feedback)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft or version not found, or version cannot be rejected"
            )

        # Get the updated draft
        updated_draft = drafting_service.get_draft(draft_id)

        if not updated_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found after rejection"
            )

        return {
            "success": True,
            "draft": updated_draft.to_dict(),
            "message": "Draft version rejected successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error rejecting draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject draft version"
        )

@router.post("/{draft_id}/versions/{version_id}/modify")
async def modify_draft_version(
    draft_id: str,
    version_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Modify a draft version with user input"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get modifications from request
        modifications = request.get("modifications", {})

        if not modifications:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Modifications are required"
            )

        # Modify draft version
        success = await drafting_service.modify_draft_version(draft_id, version_id, user_id, modifications)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft or version not found"
            )

        return {
            "success": True,
            "message": "Draft version modified successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error modifying draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to modify draft version"
        )

@router.post("/{draft_id}/versions/{version_id}/regenerate")
async def regenerate_draft_version(
    draft_id: str,
    version_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Regenerate a draft version based on user feedback"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get feedback from request
        feedback = request.get("feedback")

        # Regenerate draft version
        new_version = await drafting_service.regenerate_draft_version(draft_id, version_id, user_id, feedback)

        if not new_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft or version not found, or access denied"
            )

        # Get the updated draft
        updated_draft = drafting_service.get_draft(draft_id)

        if not updated_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found after regeneration"
            )

        return {
            "success": True,
            "draft": updated_draft.to_dict(),
            "version": new_version.to_dict(),
            "message": "Draft version regenerated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error regenerating draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate draft version"
        )

@router.get("/{draft_id}/compare")
async def compare_draft_versions(
    draft_id: str,
    version_id_1: str,
    version_id_2: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Compare two versions of a draft"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Compare versions
        comparison = drafting_service.get_draft_comparison(draft_id, version_id_1, version_id_2, user_id)

        if not comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft or versions not found, or access denied"
            )

        return {
            "success": True,
            "comparison": comparison
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error comparing draft versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare draft versions"
        )

@router.post("/{draft_id}/export")
async def export_draft(
    draft_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
):
    """Export a draft in specified format"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get export format from request
        export_format = request.get("format", "json")

        # Export draft
        export_data = drafting_service.export_draft(draft_id, user_id, export_format)

        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or access denied"
            )

        # Return appropriate response based on format
        if export_format == "json":
            # For JSON, return the data directly if it's already a dict, otherwise parse it
            if isinstance(export_data, str):
                try:
                    json_data = json.loads(export_data)
                    return {
                        "success": True,
                        "data": json_data
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "data": {"content": export_data}
                    }
            else:
                return {
                    "success": True,
                    "data": export_data
                }
        else:
            # For text-based formats, return as streaming response
            return StreamingResponse(
                io.BytesIO(export_data.encode('utf-8') if isinstance(export_data, str) else export_data),
                media_type=f"application/{export_format}",
                headers={
                    "Content-Disposition": f"attachment; filename=draft_{draft_id}.{export_format}"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting draft: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export draft"
        )

@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Delete a draft"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Delete draft
        success = drafting_service.delete_draft(draft_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or access denied"
            )

        return {
            "success": True,
            "message": "Draft deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting draft: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete draft"
        )

@router.get("/{draft_id}/versions/{version_id}")
async def get_draft_version(
    draft_id: str,
    version_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Get a specific version of a draft"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get draft
        draft = drafting_service.get_draft(draft_id)

        if not draft or draft.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or access denied"
            )

        # Find specific version
        version = next((v for v in draft.versions if v.id == version_id), None)

        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )

        return {
            "success": True,
            "version": version.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting draft version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve draft version"
        )

@router.get("/{draft_id}/versions")
async def get_draft_versions(
    draft_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Get all versions of a draft"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get draft
        draft = drafting_service.get_draft(draft_id)

        if not draft or draft.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or access denied"
            )

        return {
            "success": True,
            "versions": [version.to_dict() for version in draft.versions]
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting draft versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve draft versions"
        )