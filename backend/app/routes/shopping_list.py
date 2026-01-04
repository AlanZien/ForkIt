"""API routes for shopping list generation and management."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.auth import UserResponse
from app.models.shopping_list import (
    ShoppingListGenerateResponse,
    ShoppingListItemResponse,
    ShoppingListResponse,
    UncheckAllResponse,
)
from app.routes.auth import get_current_user
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/api/shopping-list", tags=["shopping-list"])


def get_shopping_list_service() -> ShoppingListService:
    """Dependency to get shopping list service instance."""
    return ShoppingListService()


def _get_current_week_start() -> date:
    """Get the Monday of the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.post(
    "/generate",
    response_model=ShoppingListGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_shopping_list(
    week_start: date | None = Query(
        None, description="Monday of the week (defaults to current week)"
    ),
    current_user: UserResponse = Depends(get_current_user),
    service: ShoppingListService = Depends(get_shopping_list_service),
) -> ShoppingListGenerateResponse:
    """Generate a shopping list from the week's meal plan.

    This endpoint:
    1. Deletes any existing shopping list for the specified week
    2. Fetches all meal slots for the week
    3. Retrieves recipe details from TheMealDB
    4. Aggregates ingredients with portion multiplication
    5. Creates new shopping list items

    Args:
        week_start: Monday of the week to generate list for (optional)
        current_user: Authenticated user
        service: Shopping list service

    Returns:
        Generated shopping list with items grouped by category
    """
    user_id = current_user.id

    # Default to current week if not specified
    target_week = week_start or _get_current_week_start()

    # Validate it's a Monday
    if target_week.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start must be a Monday",
        )

    try:
        result = await service.generate_list(user_id, target_week)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=ShoppingListResponse)
async def get_shopping_list(
    week_start: date | None = Query(
        None, description="Monday of the week (defaults to current week)"
    ),
    current_user: UserResponse = Depends(get_current_user),
    service: ShoppingListService = Depends(get_shopping_list_service),
) -> ShoppingListResponse:
    """Get the shopping list for a specific week.

    Returns items grouped by category with check state.

    Args:
        week_start: Monday of the week (optional, defaults to current week)
        current_user: Authenticated user
        service: Shopping list service

    Returns:
        Shopping list with items grouped by category
    """
    user_id = current_user.id

    # Default to current week if not specified
    target_week = week_start or _get_current_week_start()

    # Validate it's a Monday
    if target_week.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start must be a Monday",
        )

    return service.get_list(user_id, target_week)


@router.put("/items/{item_id}/check", response_model=ShoppingListItemResponse)
async def toggle_item_check(
    item_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: ShoppingListService = Depends(get_shopping_list_service),
) -> ShoppingListItemResponse:
    """Toggle the checked state of a shopping list item.

    Args:
        item_id: UUID of the item to toggle
        current_user: Authenticated user
        service: Shopping list service

    Returns:
        Updated shopping list item
    """
    user_id = current_user.id

    result = service.toggle_item(user_id, item_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found",
        )

    return result


@router.put("/uncheck-all", response_model=UncheckAllResponse)
async def uncheck_all_items(
    week_start: date | None = Query(
        None, description="Monday of the week (defaults to current week)"
    ),
    current_user: UserResponse = Depends(get_current_user),
    service: ShoppingListService = Depends(get_shopping_list_service),
) -> UncheckAllResponse:
    """Uncheck all items in the shopping list.

    Args:
        week_start: Monday of the week (optional, defaults to current week)
        current_user: Authenticated user
        service: Shopping list service

    Returns:
        Count of unchecked items
    """
    user_id = current_user.id

    # Default to current week if not specified
    target_week = week_start or _get_current_week_start()

    # Validate it's a Monday
    if target_week.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start must be a Monday",
        )

    count = service.uncheck_all(user_id, target_week)
    return UncheckAllResponse(
        count=count,
        message=f"{count} item(s) unchecked",
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    week_start: date | None = Query(
        None, description="Monday of the week (defaults to current week)"
    ),
    current_user: UserResponse = Depends(get_current_user),
    service: ShoppingListService = Depends(get_shopping_list_service),
) -> None:
    """Delete all items in the shopping list for a week.

    Args:
        week_start: Monday of the week (optional, defaults to current week)
        current_user: Authenticated user
        service: Shopping list service
    """
    user_id = current_user.id

    # Default to current week if not specified
    target_week = week_start or _get_current_week_start()

    # Validate it's a Monday
    if target_week.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start must be a Monday",
        )

    service.delete_list(user_id, target_week)
