"""
Document-related tools for AI agents.
"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from django.db.models import Q

from documents.models import Document
from ai.permissions import check_permission


@tool
def search_query_documents(
    query: str, limit: int = 5, config: RunnableConfig = None
) -> str:
    """
    Search the most recent LIMIT documents for the current user with maximum of 25.

    Args:
        query: string or lookup search across title or content of document
        limit: number of results (max 25)
        config: Runtime configuration containing user context

    Returns:
        str: JSON-formatted list of matching documents or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to search documents."

    # Check permissions
    if not check_permission(user_id, "read", "document"):
        return "You do not have permission to search documents."

    # Validate limit
    if limit > 25:
        limit = 25

    try:
        # Query documents
        qs = (
            Document.objects.filter(active=True)
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .order_by("-created_at")
        )

        # Serialize results
        response_data = []
        for obj in qs[:limit]:
            response_data.append({"id": obj.id, "title": obj.title})

        if not response_data:
            return f"No documents found matching '{query}'."

        # Format response
        import json

        return json.dumps(response_data, indent=2)

    except Exception as e:
        return f"Error searching documents: {str(e)}"


@tool
def list_documents(limit: int = 5, config: RunnableConfig = None) -> str:
    """
    List the most recent LIMIT documents for the current user with maximum of 25.

    Args:
        limit: number of results (max 25)
        config: Runtime configuration containing user context

    Returns:
        str: JSON-formatted list of documents or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to list documents."

    # Check permissions
    if not check_permission(user_id, "read", "document"):
        return "You do not have permission to list documents."

    # Validate limit
    if limit > 25:
        limit = 25

    try:
        # Query documents
        qs = Document.objects.filter(active=True).order_by("-created_at")

        # Serialize results
        response_data = []
        for obj in qs[:limit]:
            response_data.append({"id": obj.id, "title": obj.title})

        if not response_data:
            return "No documents found."

        # Format response
        import json

        return json.dumps(response_data, indent=2)

    except Exception as e:
        return f"Error listing documents: {str(e)}"


@tool
def get_document(document_id: int, config: RunnableConfig = None) -> str:
    """
    Get the details of a document for the current user.

    Args:
        document_id: ID of the document to retrieve
        config: Runtime configuration containing user context

    Returns:
        str: JSON-formatted document details or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to get document details."

    # Check permissions
    if not check_permission(user_id, "read", "document"):
        return "You do not have permission to view documents."

    try:
        obj = Document.objects.get(id=document_id, active=True)

        # Serialize result
        response_data = {
            "id": obj.id,
            "title": obj.title,
            "content": obj.content,
            "created_at": str(obj.created_at),
        }

        # Format response
        import json

        return json.dumps(response_data, indent=2)

    except Document.DoesNotExist:
        return f"Document {document_id} not found."
    except Exception as e:
        return f"Error retrieving document: {str(e)}"


@tool
def create_document(title: str, content: str, config: RunnableConfig = None) -> str:
    """
    Create a new document to store for the user.

    Args:
        title: string max characters of 120
        content: long form text in many paragraphs or pages
        config: Runtime configuration containing user context

    Returns:
        str: JSON-formatted created document or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to create documents."

    # Check permissions
    if not check_permission(user_id, "create", "document"):
        return "You do not have permission to create documents."

    try:
        # Create document
        obj = Document.objects.create(
            title=title, content=content, owner_id=user_id, active=True
        )

        # Serialize result
        response_data = {
            "id": obj.id,
            "title": obj.title,
            "content": obj.content,
            "created_at": str(obj.created_at),
        }

        # Format response
        import json

        return f"Document created successfully: {json.dumps(response_data, indent=2)}"

    except Exception as e:
        return f"Error creating document: {str(e)}"


@tool
def update_document(
    document_id: int,
    title: str = None,
    content: str = None,
    config: RunnableConfig = None,
) -> str:
    """
    Update a document for a user by the document id and related arguments.

    Args:
        document_id: id of document (required)
        title: string max characters of 120 (optional)
        content: long form text in many paragraphs or pages (optional)
        config: Runtime configuration containing user context

    Returns:
        str: JSON-formatted updated document or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to update documents."

    # Check permissions
    if not check_permission(user_id, "update", "document"):
        return "You do not have permission to update documents."

    if title is None and content is None:
        return "Error: Please provide at least title or content to update."

    try:
        # Get document (check ownership)
        obj = Document.objects.get(id=document_id, owner_id=user_id, active=True)

        # Update fields
        if title is not None:
            obj.title = title
        if content is not None:
            obj.content = content

        if title or content:
            obj.save()

        # Serialize result
        response_data = {
            "id": obj.id,
            "title": obj.title,
            "content": obj.content,
            "created_at": str(obj.created_at),
        }

        # Format response
        import json

        return f"Document updated successfully: {json.dumps(response_data, indent=2)}"

    except Document.DoesNotExist:
        return f"Document {document_id} not found or you don't have permission to update it."
    except Exception as e:
        return f"Error updating document: {str(e)}"


@tool
def delete_document(document_id: int, config: RunnableConfig = None) -> str:
    """
    Delete the document for the current user by document_id.

    Args:
        document_id: ID of the document to delete
        config: Runtime configuration containing user context

    Returns:
        str: Success message or error message
    """
    # Extract user context
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if user_id is None:
        return "Error: User authentication required to delete documents."

    # Check permissions
    if not check_permission(user_id, "delete", "document"):
        return "You do not have permission to delete documents."

    try:
        # Get document (check ownership)
        obj = Document.objects.get(id=document_id, owner_id=user_id, active=True)

        # Soft delete (set active=False)
        obj.active = False
        obj.save()

        return f"Document {document_id} deleted successfully."

    except Document.DoesNotExist:
        return f"Document {document_id} not found or you don't have permission to delete it."
    except Exception as e:
        return f"Error deleting document: {str(e)}"


# Export all document tools
document_tools = [
    search_query_documents,
    list_documents,
    get_document,
    create_document,
    update_document,
    delete_document,
]
