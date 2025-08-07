from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import logging
import io

from backend.api.services.workflow_service import WorkflowService
from backend.api.endpoints.auth import verify_supabase_jwt

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Initialize workflow service
workflow_service = WorkflowService()

@router.get("/")
async def get_workflows(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)) -> Dict[str, Any]:
    """Get all workflows for the authenticated user"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get user's workflows
        workflows = workflow_service.get_user_workflows(user_id)

        return {
            "success": True,
            "workflows": [workflow.to_dict() for workflow in workflows]
        }

    except Exception as e:
        logging.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflows"
        )

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, user_data: Dict[str, Any] = Depends(verify_supabase_jwt)) -> Dict[str, Any]:
    """Get a specific workflow by ID"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return {
            "success": True,
            "workflow": workflow.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow"
        )

@router.post("/create-from-chat")
async def create_workflow_from_chat(
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Create a new workflow from an existing chat"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        chat_id = request.get("chat_id")
        if not chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="chat_id is required"
            )

        # Create workflow from chat
        workflow = workflow_service.create_workflow_from_chat(user_id, chat_id)

        return {
            "success": True,
            "workflow": workflow.to_dict(),
            "message": "Workflow created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating workflow from chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow"
        )

@router.post("/{workflow_id}/control")
async def control_workflow(
    workflow_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Control workflow execution (start, pause, resume, stop)"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        action = request.get("action")
        if not action or action not in ["start", "pause", "resume", "stop"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid action (start, pause, resume, stop) is required"
            )

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Control workflow
        updated_workflow = workflow_service.control_workflow(workflow_id, action)

        if not updated_workflow:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to control workflow"
            )

        return {
            "success": True,
            "workflow": updated_workflow.to_dict(),
            "message": f"Workflow {action}ed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error controlling workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to control workflow"
        )

@router.post("/{workflow_id}/steps/{step_id}/approve")
async def approve_step(
    workflow_id: str,
    step_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Approve a completed workflow step"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Approve step
        updated_workflow = workflow_service.approve_step(workflow_id, step_id)

        if not updated_workflow:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve step"
            )

        return {
            "success": True,
            "workflow": updated_workflow.to_dict(),
            "message": "Step approved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error approving step {step_id} in workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve step"
        )

@router.post("/{workflow_id}/steps/{step_id}/modify")
async def modify_step(
    workflow_id: str,
    step_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Modify a workflow step with user input"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        modifications = request.get("modifications", {})

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Modify step
        updated_workflow = workflow_service.modify_step(workflow_id, step_id, modifications)

        if not updated_workflow:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to modify step"
            )

        return {
            "success": True,
            "workflow": updated_workflow.to_dict(),
            "message": "Step modified successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error modifying step {step_id} in workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to modify step"
        )

@router.post("/{workflow_id}/export")
async def export_workflow(
    workflow_id: str,
    request: Dict[str, Any],
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
):
    """Export workflow results in specified format"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        export_format = request.get("format", "json")
        if export_format not in ["json", "pdf", "docx"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid format (json, pdf, docx) is required"
            )

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Export workflow
        export_data = workflow_service.export_workflow(workflow_id, export_format)

        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export workflow"
            )

        # Determine content type and filename
        content_types = {
            "json": "application/json",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

        filenames = {
            "json": f"workflow-{workflow_id}.json",
            "pdf": f"workflow-{workflow_id}.pdf",
            "docx": f"workflow-{workflow_id}.docx"
        }

        return StreamingResponse(
            io.BytesIO(export_data),
            media_type=content_types[export_format],
            headers={"Content-Disposition": f"attachment; filename={filenames[export_format]}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export workflow"
        )

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Delete a workflow"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Get workflow
        workflow = workflow_service.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user owns this workflow
        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Delete workflow (remove from storage)
        from backend.api.services.workflow_service import WORKFLOW_STORAGE
        if workflow_id in WORKFLOW_STORAGE:
            del WORKFLOW_STORAGE[workflow_id]

        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workflow"
        )

@router.post("/{workflow_id}/create-draft")
async def create_draft_from_workflow(
    workflow_id: str,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
) -> Dict[str, Any]:
    """Create a draft from an existing workflow"""
    try:
        # Get user info from verified JWT
        user_id = user_data.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )

        # Create draft from workflow
        draft_id = workflow_service.create_draft_from_workflow(workflow_id, user_id)

        if not draft_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found or access denied"
            )

        return {
            "success": True,
            "draft_id": draft_id,
            "message": "Draft created from workflow successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating draft from workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create draft from workflow"
        )