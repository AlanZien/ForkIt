"""API routes for weekly meal planning slots."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.auth import UserResponse
from app.models.meal_slot import (
    MealSlotCreate,
    MealSlotResponse,
    MealSlotUpdate,
    MealType,
    RecentRecipeResponse,
    WeekSlotsResponse,
)
from app.routes.auth import get_current_user
from app.services.meal_slots_service import MealSlotsService

router = APIRouter(prefix="/api/meal-slots", tags=["meal-slots"])


def get_meal_slots_service() -> MealSlotsService:
    """Dependency to get meal slots service instance."""
    return MealSlotsService()


@router.get("", response_model=WeekSlotsResponse)
async def get_week_slots(
    week_start: date = Query(
        ..., description="Monday of the week to fetch (YYYY-MM-DD)"
    ),
    current_user: UserResponse = Depends(get_current_user),
    service: MealSlotsService = Depends(get_meal_slots_service),
) -> WeekSlotsResponse:
    """Get all meal slots for a specific week.

    Args:
        week_start: Monday of the week (ISO date format)
        current_user: Authenticated user
        service: Meal slots service

    Returns:
        List of meal slots for the week
    """
    user_id = current_user.id

    try:
        slots = service.get_week_slots(user_id, week_start)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    week_end = week_start + timedelta(days=6)

    return WeekSlotsResponse(
        slots=slots,
        week_start=week_start,
        week_end=week_end,
    )


@router.get("/recent", response_model=list[RecentRecipeResponse])
async def get_recent_recipes(
    current_user: UserResponse = Depends(get_current_user),
    service: MealSlotsService = Depends(get_meal_slots_service),
) -> list[RecentRecipeResponse]:
    """Get the most recent unique recipes used by the user.

    Returns:
        List of up to 10 recent recipes
    """
    user_id = current_user.id
    return service.get_recent_recipes(user_id)


@router.post("", response_model=MealSlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    data: MealSlotCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: MealSlotsService = Depends(get_meal_slots_service),
) -> MealSlotResponse:
    """Create a new meal slot.

    Args:
        data: Meal slot creation data
        current_user: Authenticated user
        service: Meal slots service

    Returns:
        The created meal slot
    """
    user_id = current_user.id

    try:
        return service.create_slot(user_id, data)
    except ValueError as e:
        error_message = str(e)
        if "already exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from e


@router.put("/{slot_date}/{meal_type}", response_model=MealSlotResponse)
async def update_slot(
    slot_date: date,
    meal_type: MealType,
    data: MealSlotUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: MealSlotsService = Depends(get_meal_slots_service),
) -> MealSlotResponse:
    """Update an existing meal slot.

    Args:
        slot_date: Date of the slot (YYYY-MM-DD)
        meal_type: Type of meal (dejeuner or diner)
        data: Update data
        current_user: Authenticated user
        service: Meal slots service

    Returns:
        The updated meal slot
    """
    user_id = current_user.id

    result = service.update_slot(user_id, slot_date, meal_type, data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal slot not found",
        )

    return result


@router.delete("/{slot_date}/{meal_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_date: date,
    meal_type: MealType,
    current_user: UserResponse = Depends(get_current_user),
    service: MealSlotsService = Depends(get_meal_slots_service),
) -> None:
    """Delete a meal slot.

    Args:
        slot_date: Date of the slot (YYYY-MM-DD)
        meal_type: Type of meal (dejeuner or diner)
        current_user: Authenticated user
        service: Meal slots service
    """
    user_id = current_user.id

    deleted = service.delete_slot(user_id, slot_date, meal_type)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal slot not found",
        )
