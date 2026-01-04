"""Service for managing user meal planning slots."""

from datetime import date, timedelta

from app.models.meal_slot import (
    MealSlotCreate,
    MealSlotResponse,
    MealSlotUpdate,
    MealType,
    RecentRecipeResponse,
)
from app.services.supabase import get_supabase_admin


class MealSlotsService:
    """Service for CRUD operations on meal planning slots."""

    # Maximum weeks ahead that users can plan
    MAX_WEEKS_AHEAD = 4

    def __init__(self) -> None:
        """Initialize the meal slots service."""
        self.client = get_supabase_admin()
        self.table = "meal_slots"

    def _get_monday_of_week(self, d: date) -> date:
        """Get the Monday of the week for a given date."""
        return d - timedelta(days=d.weekday())

    def _validate_date_range(self, d: date) -> None:
        """Validate that date is within allowed range.

        Args:
            d: Date to validate

        Raises:
            ValueError: If date is in the past or beyond 4 weeks
        """
        today = date.today()
        if d < today:
            raise ValueError("Cannot access past dates")

        # Calculate the maximum allowed date (4 weeks from current week's Monday)
        current_week_monday = self._get_monday_of_week(today)
        max_week_monday = current_week_monday + timedelta(weeks=self.MAX_WEEKS_AHEAD)
        max_date = max_week_monday + timedelta(days=6)  # Sunday of max week

        if d > max_date:
            raise ValueError("Cannot access beyond 4 weeks ahead")

    def _validate_week_start(self, week_start: date) -> None:
        """Validate that week_start is a Monday and within range.

        Args:
            week_start: The Monday to validate

        Raises:
            ValueError: If not a Monday or outside allowed range
        """
        if week_start.weekday() != 0:
            raise ValueError("week_start must be a Monday")

        today = date.today()
        current_week_monday = self._get_monday_of_week(today)

        if week_start < current_week_monday:
            raise ValueError("Cannot access past weeks")

        max_week_monday = current_week_monday + timedelta(weeks=self.MAX_WEEKS_AHEAD)
        if week_start > max_week_monday:
            raise ValueError("Cannot access beyond 4 weeks ahead")

    def get_week_slots(self, user_id: str, week_start: date) -> list[MealSlotResponse]:
        """Get all meal slots for a user for a specific week.

        Args:
            user_id: The user's UUID
            week_start: Monday of the week (ISO format date)

        Returns:
            List of meal slots for the week (0-14 slots)
        """
        self._validate_week_start(week_start)

        week_end = week_start + timedelta(days=6)

        response = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .gte("date", week_start.isoformat())
            .lte("date", week_end.isoformat())
            .order("date")
            .order("meal_type")
            .execute()
        )

        return [
            MealSlotResponse(
                id=str(row["id"]),
                user_id=row["user_id"],
                slot_date=row["date"],
                meal_type=MealType(row["meal_type"]),
                recipe_id=row["recipe_id"],
                recipe_name=row["recipe_name"],
                recipe_thumbnail=row.get("recipe_thumbnail"),
                portions=row["portions"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in response.data
        ]

    def get_slot(
        self, user_id: str, slot_date: date, meal_type: MealType
    ) -> MealSlotResponse | None:
        """Get a single meal slot.

        Args:
            user_id: The user's UUID
            slot_date: The date of the slot
            meal_type: The meal type (dejeuner or diner)

        Returns:
            The meal slot or None if not found
        """
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("date", slot_date.isoformat())
            .eq("meal_type", meal_type.value)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]
        return MealSlotResponse(
            id=str(row["id"]),
            user_id=row["user_id"],
            slot_date=row["date"],
            meal_type=MealType(row["meal_type"]),
            recipe_id=row["recipe_id"],
            recipe_name=row["recipe_name"],
            recipe_thumbnail=row.get("recipe_thumbnail"),
            portions=row["portions"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_slot(
        self, user_id: str, data: MealSlotCreate, default_portions: int = 2
    ) -> MealSlotResponse:
        """Create a new meal slot.

        Args:
            user_id: The user's UUID
            data: Meal slot creation data
            default_portions: Default portions if not provided

        Returns:
            The created meal slot

        Raises:
            ValueError: If slot already exists for this date/meal_type
        """
        self._validate_date_range(data.slot_date)

        # Check if slot already exists
        existing = self.get_slot(user_id, data.slot_date, data.meal_type)
        if existing:
            raise ValueError("Slot already exists for this date and meal type")

        portions = data.portions if data.portions is not None else default_portions

        response = (
            self.client.table(self.table)
            .insert(
                {
                    "user_id": user_id,
                    "date": data.slot_date.isoformat(),
                    "meal_type": data.meal_type.value,
                    "recipe_id": data.recipe_id,
                    "recipe_name": data.recipe_name,
                    "recipe_thumbnail": data.recipe_thumbnail,
                    "portions": portions,
                }
            )
            .execute()
        )

        row = response.data[0]
        return MealSlotResponse(
            id=str(row["id"]),
            user_id=row["user_id"],
            slot_date=row["date"],
            meal_type=MealType(row["meal_type"]),
            recipe_id=row["recipe_id"],
            recipe_name=row["recipe_name"],
            recipe_thumbnail=row.get("recipe_thumbnail"),
            portions=row["portions"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_slot(
        self,
        user_id: str,
        slot_date: date,
        meal_type: MealType,
        data: MealSlotUpdate,
    ) -> MealSlotResponse | None:
        """Update an existing meal slot.

        Args:
            user_id: The user's UUID
            slot_date: The date of the slot
            meal_type: The meal type (dejeuner or diner)
            data: Update data

        Returns:
            The updated meal slot or None if not found
        """
        # Check if slot exists
        existing = self.get_slot(user_id, slot_date, meal_type)
        if not existing:
            return None

        # Build update dict with only provided fields
        update_data: dict = {}
        if data.recipe_id is not None:
            update_data["recipe_id"] = data.recipe_id
        if data.recipe_name is not None:
            update_data["recipe_name"] = data.recipe_name
        if data.recipe_thumbnail is not None:
            update_data["recipe_thumbnail"] = data.recipe_thumbnail
        if data.portions is not None:
            update_data["portions"] = data.portions

        if not update_data:
            return existing

        response = (
            self.client.table(self.table)
            .update(update_data)
            .eq("user_id", user_id)
            .eq("date", slot_date.isoformat())
            .eq("meal_type", meal_type.value)
            .execute()
        )

        row = response.data[0]
        return MealSlotResponse(
            id=str(row["id"]),
            user_id=row["user_id"],
            slot_date=row["date"],
            meal_type=MealType(row["meal_type"]),
            recipe_id=row["recipe_id"],
            recipe_name=row["recipe_name"],
            recipe_thumbnail=row.get("recipe_thumbnail"),
            portions=row["portions"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def delete_slot(self, user_id: str, slot_date: date, meal_type: MealType) -> bool:
        """Delete a meal slot.

        Args:
            user_id: The user's UUID
            slot_date: The date of the slot
            meal_type: The meal type (dejeuner or diner)

        Returns:
            True if deleted, False if not found
        """
        # Check if slot exists first
        existing = self.get_slot(user_id, slot_date, meal_type)
        if not existing:
            return False

        self.client.table(self.table).delete().eq("user_id", user_id).eq(
            "date", slot_date.isoformat()
        ).eq("meal_type", meal_type.value).execute()

        return True

    def get_recent_recipes(
        self, user_id: str, limit: int = 10
    ) -> list[RecentRecipeResponse]:
        """Get the most recent unique recipes used by the user.

        Args:
            user_id: The user's UUID
            limit: Maximum number of recipes to return (default 10)

        Returns:
            List of recent recipes ordered by last used date
        """
        # Get all slots ordered by created_at desc, then deduplicate by recipe_id
        response = (
            self.client.table(self.table)
            .select("recipe_id, recipe_name, recipe_thumbnail, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        # Deduplicate by recipe_id keeping most recent
        seen_recipes: set[str] = set()
        recent_recipes: list[RecentRecipeResponse] = []

        for row in response.data:
            recipe_id = row["recipe_id"]
            if recipe_id not in seen_recipes:
                seen_recipes.add(recipe_id)
                recent_recipes.append(
                    RecentRecipeResponse(
                        recipe_id=recipe_id,
                        recipe_name=row["recipe_name"],
                        recipe_thumbnail=row.get("recipe_thumbnail"),
                        last_used=row["created_at"],
                    )
                )
                if len(recent_recipes) >= limit:
                    break

        return recent_recipes
