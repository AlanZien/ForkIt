"""Recipe models for TheMealDB API responses."""

from pydantic import BaseModel, ConfigDict


class Ingredient(BaseModel):
    """Ingredient with measurement."""

    name: str
    measure: str


class RecipeSummary(BaseModel):
    """Summary recipe for list views (from filter endpoint)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    thumbnail: str


class UnifiedRecipeSummary(BaseModel):
    """Recipe summary with source field for unified search results."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    thumbnail: str
    source: str  # "personal" or "api"


class Recipe(BaseModel):
    """Full recipe details."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    category: str | None = None
    area: str | None = None
    instructions: str | None = None
    thumbnail: str | None = None
    tags: str | None = None
    youtube: str | None = None
    source: str | None = None
    ingredients: list[Ingredient] = []

    @classmethod
    def from_api_response(cls, data: dict) -> "Recipe":
        """Parse TheMealDB API response into Recipe model."""
        ingredients: list[Ingredient] = []

        for i in range(1, 21):
            ingredient_name = data.get(f"strIngredient{i}")
            measure = data.get(f"strMeasure{i}")

            if ingredient_name and ingredient_name.strip():
                ingredients.append(
                    Ingredient(
                        name=ingredient_name.strip(),
                        measure=measure.strip() if measure else "",
                    )
                )

        return cls(
            id=data.get("idMeal", ""),
            name=data.get("strMeal", ""),
            category=data.get("strCategory"),
            area=data.get("strArea"),
            instructions=data.get("strInstructions"),
            thumbnail=data.get("strMealThumb"),
            tags=data.get("strTags"),
            youtube=data.get("strYoutube"),
            source=data.get("strSource"),
            ingredients=ingredients,
        )


class Category(BaseModel):
    """Meal category."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    thumbnail: str
    description: str


class RecipeListResponse(BaseModel):
    """Response for recipe list endpoints."""

    recipes: list[RecipeSummary]


class UnifiedSearchResponse(BaseModel):
    """Response for unified search endpoint with personal + API recipes."""

    recipes: list[UnifiedRecipeSummary]
    personal_count: int
    api_count: int


class RecipeDetailResponse(BaseModel):
    """Response for recipe detail endpoint."""

    recipe: Recipe | None


class CategoryListResponse(BaseModel):
    """Response for categories endpoint."""

    categories: list[Category]
