"""API routes for personal recipe management.

This module provides CRUD endpoints for user's personal recipes,
including the ability to fork recipes from TheMealDB API.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.models.auth import UserResponse
from app.models.personal_recipe import (
    PersonalRecipeCreate,
    PersonalRecipeListResponse,
    PersonalRecipeResponse,
    PersonalRecipeUpdate,
)
from app.routes.auth import get_current_user
from app.services.personal_recipes_service import PersonalRecipesService
from app.services.supabase import get_supabase_admin

router = APIRouter(prefix="/api/personal-recipes", tags=["personal-recipes"])

# Image upload constants
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
STORAGE_BUCKET = "recipe-images"


class ImageUploadResponse(BaseModel):
    """Response for successful image upload."""

    url: str
    filename: str


def get_personal_recipes_service() -> PersonalRecipesService:
    """Dependency to get personal recipes service instance."""
    return PersonalRecipesService()


@router.post(
    "",
    response_model=PersonalRecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    data: PersonalRecipeCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> PersonalRecipeResponse:
    """Create a new personal recipe.

    Creates a personal recipe with nested ingredients and steps in a single request.
    Validates required fields: title, servings (1-20), at least one ingredient,
    and at least one instruction step.

    Args:
        data: Recipe creation data with nested ingredients and steps.
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Returns:
        Created recipe with id, user_id, created_at, and nested data.

    Raises:
        HTTPException: 422 if validation fails.
    """
    user_id = current_user.id

    try:
        return service.create_recipe(user_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create recipe: {e!s}",
        ) from e


@router.get("", response_model=PersonalRecipeListResponse)
async def list_recipes(
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> PersonalRecipeListResponse:
    """List all personal recipes for the current user.

    Returns recipe summaries (without nested ingredients/steps) for list view.
    Results are ordered by created_at descending (newest first).

    Args:
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Returns:
        List of recipe summaries with count.
    """
    user_id = current_user.id
    recipes = service.get_recipes(user_id)

    return PersonalRecipeListResponse(recipes=recipes, count=len(recipes))


@router.get("/{recipe_id}", response_model=PersonalRecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> PersonalRecipeResponse:
    """Get a single personal recipe by ID.

    Returns the full recipe with nested ingredients and steps.
    Ingredients are ordered by sort_order, steps by step_number.

    Args:
        recipe_id: The recipe's UUID.
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Returns:
        Full recipe with nested ingredients and steps.

    Raises:
        HTTPException: 404 if recipe not found or not owned by user.
    """
    user_id = current_user.id
    recipe = service.get_recipe_by_id(user_id, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


@router.put("/{recipe_id}", response_model=PersonalRecipeResponse)
async def update_recipe(
    recipe_id: str,
    data: PersonalRecipeUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> PersonalRecipeResponse:
    """Update an existing personal recipe.

    Supports partial updates - only provided fields are updated.
    If ingredients or steps are provided, they replace the existing ones entirely.

    Args:
        recipe_id: The recipe's UUID.
        data: Update data with optional fields.
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Returns:
        Updated recipe with all nested data.

    Raises:
        HTTPException: 404 if recipe not found or not owned by user.
    """
    user_id = current_user.id
    recipe = service.update_recipe(user_id, recipe_id, data)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> None:
    """Delete a personal recipe.

    Deletes the recipe and all associated ingredients and steps (cascade).

    Args:
        recipe_id: The recipe's UUID.
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Raises:
        HTTPException: 404 if recipe not found or not owned by user.
    """
    user_id = current_user.id
    success = service.delete_recipe(user_id, recipe_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )


@router.post(
    "/upload-image",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_recipe_image(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
) -> ImageUploadResponse:
    """Upload an image for a personal recipe.

    Uploads the image to Supabase Storage under the user's folder.
    Returns the URL that can be used as image_url when creating/updating recipes.

    Args:
        file: The image file to upload.
        current_user: Current authenticated user.

    Returns:
        ImageUploadResponse with the uploaded image URL.

    Raises:
        HTTPException: 400 if file type or size is invalid.
        HTTPException: 500 if upload fails.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024 * 1024)}MB",
        )

    # Generate unique filename
    extension = file.content_type.split("/")[1]
    if extension == "jpeg":
        extension = "jpg"
    filename = f"{uuid.uuid4()}.{extension}"
    storage_path = f"{current_user.id}/{filename}"

    # Upload to Supabase Storage
    try:
        supabase = get_supabase_admin()
        result = supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type},
        )

        # Get the public URL
        url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)

        return ImageUploadResponse(url=url, filename=filename)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e!s}",
        ) from e


@router.post(
    "/fork/{api_recipe_id}",
    response_model=PersonalRecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def fork_recipe(
    api_recipe_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: PersonalRecipesService = Depends(get_personal_recipes_service),
) -> PersonalRecipeResponse:
    """Fork a recipe from TheMealDB API as a personal recipe.

    Fetches the original recipe from TheMealDB, transforms it to the personal
    recipe structure, and stores it with source_recipe_id for traceability.

    Ingredient parsing is best-effort:
    - Simple formats: "2 cups" -> quantity=2, unit="cups"
    - Fractions: "1/2 cup" -> quantity=0.5, unit="cup"
    - Complex: "to taste" -> quantity=1, unit="", note="to taste"

    Args:
        api_recipe_id: The TheMealDB recipe ID.
        current_user: Current authenticated user.
        service: Personal recipes service instance.

    Returns:
        Created personal recipe with source_recipe_id set.

    Raises:
        HTTPException: 404 if API recipe not found, 503 if API unavailable.
    """
    user_id = current_user.id

    try:
        return await service.fork_recipe(user_id, api_recipe_id)
    except Exception as e:
        # Use class name check for robustness during module reloading in tests
        exc_name = type(e).__name__
        if exc_name == "RecipeNotFoundError":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API recipe not found: {api_recipe_id}",
            ) from e
        elif exc_name == "ExternalAPIError":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="External API unavailable",
            ) from e
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="External API unavailable",
            ) from e
