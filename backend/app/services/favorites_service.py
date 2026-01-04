"""Service for managing user favorite recipes."""

from app.models.favorite import FavoriteCreate, FavoriteResponse
from app.services.supabase import get_supabase_admin


class FavoritesService:
    """Service for CRUD operations on user favorites."""

    def __init__(self) -> None:
        """Initialize the favorites service."""
        self.client = get_supabase_admin()
        self.table = "user_favorites"

    def get_favorites(self, user_id: str) -> list[FavoriteResponse]:
        """Get all favorites for a user.

        Args:
            user_id: The user's UUID

        Returns:
            List of favorite recipes
        """
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [
            FavoriteResponse(
                id=str(row["id"]),
                recipe_id=row["recipe_id"],
                recipe_name=row["recipe_name"],
                recipe_thumbnail=row.get("recipe_thumbnail"),
                created_at=row["created_at"],
            )
            for row in response.data
        ]

    def add_favorite(self, user_id: str, data: FavoriteCreate) -> FavoriteResponse:
        """Add a recipe to user's favorites.

        Args:
            user_id: The user's UUID
            data: Favorite creation data

        Returns:
            The created favorite
        """
        # Check if already exists
        existing = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("recipe_id", data.recipe_id)
            .execute()
        )

        if existing.data:
            # Return existing favorite
            row = existing.data[0]
            return FavoriteResponse(
                id=str(row["id"]),
                recipe_id=row["recipe_id"],
                recipe_name=row["recipe_name"],
                recipe_thumbnail=row.get("recipe_thumbnail"),
                created_at=row["created_at"],
            )

        # Insert new favorite
        response = (
            self.client.table(self.table)
            .insert(
                {
                    "user_id": user_id,
                    "recipe_id": data.recipe_id,
                    "recipe_name": data.recipe_name,
                    "recipe_thumbnail": data.recipe_thumbnail,
                }
            )
            .execute()
        )

        row = response.data[0]
        return FavoriteResponse(
            id=str(row["id"]),
            recipe_id=row["recipe_id"],
            recipe_name=row["recipe_name"],
            recipe_thumbnail=row.get("recipe_thumbnail"),
            created_at=row["created_at"],
        )

    def remove_favorite(self, user_id: str, recipe_id: str) -> bool:
        """Remove a recipe from user's favorites.

        Args:
            user_id: The user's UUID
            recipe_id: The recipe ID to remove

        Returns:
            True (idempotent - always succeeds)
        """
        self.client.table(self.table).delete().eq("user_id", user_id).eq(
            "recipe_id", recipe_id
        ).execute()

        return True

    def is_favorite(self, user_id: str, recipe_id: str) -> bool:
        """Check if a recipe is in user's favorites.

        Args:
            user_id: The user's UUID
            recipe_id: The recipe ID to check

        Returns:
            True if recipe is a favorite
        """
        response = (
            self.client.table(self.table)
            .select("id")
            .eq("user_id", user_id)
            .eq("recipe_id", recipe_id)
            .execute()
        )

        return len(response.data) > 0
