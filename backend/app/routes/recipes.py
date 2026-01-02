"""Recipe API routes."""

from fastapi import APIRouter, HTTPException, Query

from app.models.recipe import (
    Category,
    CategoryListResponse,
    Recipe,
    RecipeDetailResponse,
    RecipeListResponse,
    RecipeSummary,
)
from app.services.themealdb import themealdb_client

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("/search", response_model=RecipeListResponse)
async def search_recipes(q: str = Query(..., min_length=1, description="Search query")):
    """Search recipes by name."""
    response = await themealdb_client.search_by_name(q)
    meals = response.get("meals") or []

    recipes = [
        RecipeSummary(
            id=meal["idMeal"],
            name=meal["strMeal"],
            thumbnail=meal["strMealThumb"],
        )
        for meal in meals
    ]

    return RecipeListResponse(recipes=recipes)


@router.get("/random", response_model=RecipeDetailResponse)
async def get_random_recipe():
    """Get a random recipe."""
    response = await themealdb_client.get_random()
    meals = response.get("meals") or []

    if not meals:
        return RecipeDetailResponse(recipe=None)

    recipe = Recipe.from_api_response(meals[0])
    return RecipeDetailResponse(recipe=recipe)


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories():
    """List all recipe categories."""
    response = await themealdb_client.list_categories()
    categories_data = response.get("categories") or []

    categories = [
        Category(
            id=cat["idCategory"],
            name=cat["strCategory"],
            thumbnail=cat["strCategoryThumb"],
            description=cat["strCategoryDescription"],
        )
        for cat in categories_data
    ]

    return CategoryListResponse(categories=categories)


@router.get("/category/{category_name}", response_model=RecipeListResponse)
async def get_recipes_by_category(category_name: str):
    """Get recipes by category."""
    response = await themealdb_client.filter_by_category(category_name)
    meals = response.get("meals") or []

    recipes = [
        RecipeSummary(
            id=meal["idMeal"],
            name=meal["strMeal"],
            thumbnail=meal["strMealThumb"],
        )
        for meal in meals
    ]

    return RecipeListResponse(recipes=recipes)


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe_by_id(recipe_id: str):
    """Get recipe details by ID."""
    response = await themealdb_client.get_by_id(recipe_id)
    meals = response.get("meals") or []

    if not meals:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = Recipe.from_api_response(meals[0])
    return RecipeDetailResponse(recipe=recipe)
