from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.dependencies import get_current_user
from auth.database import (
    get_user,
    create_chat,
    get_user_chats,
    get_chat,
    add_message,
    get_chat_messages,
    delete_chat
)


router = APIRouter(
    prefix="/history",
    tags=["Chat History"]
)


class CreateChatRequest(BaseModel):
    title: str = "New Chat"


class AddMessageRequest(BaseModel):
    role: str
    content: str


# -----------------------------
# CREATE NEW CHAT
# -----------------------------

@router.post("/chats")
def create_new_chat(
    data: CreateChatRequest,
    current_user: dict = Depends(get_current_user)
):
    user = get_user(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    chat_id = create_chat(
        user_id=user["id"],
        title=data.title
    )

    return {
        "message": "Chat created successfully",
        "chat_id": chat_id,
        "title": data.title
    }


# -----------------------------
# GET CHAT HISTORY
# -----------------------------

@router.get("/chats")
def list_chats(
    current_user: dict = Depends(get_current_user)
):
    user = get_user(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    chats = get_user_chats(user["id"])

    return {
        "chats": chats
    }


# -----------------------------
# GET ONE CHAT
# -----------------------------

@router.get("/chats/{chat_id}")
def get_one_chat(
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    user = get_user(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    chat = get_chat(
        chat_id=chat_id,
        user_id=user["id"]
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    messages = get_chat_messages(
        chat_id=chat_id,
        user_id=user["id"]
    )

    return {
        "chat": chat,
        "messages": messages
    }


# -----------------------------
# ADD MESSAGE
# -----------------------------

@router.post("/chats/{chat_id}/messages")
def save_message(
    chat_id: int,
    data: AddMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    user = get_user(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    chat = get_chat(
        chat_id=chat_id,
        user_id=user["id"]
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    if data.role not in ["user", "assistant"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be user or assistant"
        )

    if not data.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    add_message(
        chat_id=chat_id,
        role=data.role,
        content=data.content
    )

    return {
        "message": "Message saved successfully"
    }


# -----------------------------
# DELETE CHAT
# -----------------------------

@router.delete("/chats/{chat_id}")
def remove_chat(
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    user = get_user(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    deleted = delete_chat(
        chat_id=chat_id,
        user_id=user["id"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    return {
        "message": "Chat deleted successfully"
    }