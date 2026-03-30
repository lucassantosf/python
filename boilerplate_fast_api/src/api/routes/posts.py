from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from src.modules.posts.schemas import PostCreate, PostUpdate, PostResponse
from src.modules.posts.service import PostService
from src.modules.posts.dependencies import get_post_service
from src.api.dependencies.auth import get_current_user_id
from src.core.domain.exceptions import NotFoundException
from src.infrastructure.tasks.post_tasks import generate_fake_post_task

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
def list_posts(
    post_service: PostService = Depends(get_post_service),
):
    """Returns all posts. Public endpoint."""
    return post_service.get_all()


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
):
    """Returns a single post by ID. Public endpoint."""
    try:
        return post_service.get_by_id(post_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    data: PostCreate,
    current_user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Creates a new post. Requires authentication — the author_id is taken from the JWT."""
    return post_service.create(
        title=data.title,
        content=data.content,
        author_id=int(current_user_id),
    )


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def request_post_generation(
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
):
    """Schedules a task to generate a fake post using background tasks."""
    background_tasks.add_task(generate_fake_post_task, int(current_user_id))
    return {"message": "Processamento do job em background iniciado com sucesso."}


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Updates a post. Requires authentication — only the post author may update it."""
    try:
        return post_service.update(
            post_id=post_id,
            title=data.title,
            content=data.content,
            author_id=int(current_user_id),
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Deletes a post. Requires authentication — only the post author may delete it."""
    try:
        post_service.delete(post_id=post_id, author_id=int(current_user_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
