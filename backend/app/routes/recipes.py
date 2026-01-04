"""Recipe API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.auth import UserResponse
from app.models.recipe import (
    Category,
    CategoryListResponse,
    Recipe,
    RecipeDetailResponse,
    RecipeListResponse,
    RecipeSummary,
    UnifiedRecipeSummary,
    UnifiedSearchResponse,
)
from app.routes.auth import get_optional_user
from app.services.personal_recipes_service import PersonalRecipesService
from app.services.preferences_service import PreferencesService
from app.services.recipe_filter_service import RecipeFilterService
from app.services.themealdb import themealdb_client

router = APIRouter(prefix="/api/recipes", tags=["recipes"])
logger = logging.getLogger(__name__)

MAX_RANDOM_ATTEMPTS = 10


def get_preferences_service() -> PreferencesService:
    """Dependency to get preferences service instance."""
    return PreferencesService()


def get_personal_recipes_service() -> PersonalRecipesService:
    """Dependency to get personal recipes service instance."""
    return PersonalRecipesService()


@router.get("/unified-search", response_model=UnifiedSearchResponse)
async def unified_search_recipes(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: UserResponse | None = Depends(get_optional_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
    personal_recipes_service: PersonalRecipesService = Depends(
        get_personal_recipes_service
    ),
):
    """Search recipes across personal recipes and TheMealDB API.

    Personal recipes are returned first, then API recipes.
    If user is authenticated, filters API results based on their preferences.
    """
    unified_results: list[UnifiedRecipeSummary] = []
    personal_count = 0
    api_count = 0

    # Search personal recipes if user is authenticated
    if current_user:
        personal_results = personal_recipes_service.search_recipes(
            current_user.id, q
        )
        personal_count = len(personal_results)
        for recipe in personal_results:
            unified_results.append(
                UnifiedRecipeSummary(
                    id=recipe.id,
                    name=recipe.title,
                    thumbnail=recipe.image_url or "",
                    source="personal",
                )
            )

    # Search TheMealDB API
    response = await themealdb_client.search_by_name(q)
    meals = response.get("meals") or []

    # Convert to Recipe objects for filtering
    recipes = [Recipe.from_api_response(meal) for meal in meals]

    # Apply filtering if user is authenticated
    if current_user:
        preferences = preferences_service.get_preferences(current_user.id)
        recipes = RecipeFilterService.filter_recipes(recipes, preferences)

    api_count = len(recipes)
    for recipe in recipes:
        unified_results.append(
            UnifiedRecipeSummary(
                id=recipe.id,
                name=recipe.name,
                thumbnail=recipe.thumbnail or "",
                source="api",
            )
        )

    return UnifiedSearchResponse(
        recipes=unified_results,
        personal_count=personal_count,
        api_count=api_count,
    )


@router.get("/search", response_model=RecipeListResponse)
async def search_recipes(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: UserResponse | None = Depends(get_optional_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
):
    """Search recipes by name.

    If user is authenticated, filters results based on their preferences.
    """
    response = await themealdb_client.search_by_name(q)
    meals = response.get("meals") or []

    # Convert to Recipe objects for filtering
    recipes = [Recipe.from_api_response(meal) for meal in meals]

    # Apply filtering if user is authenticated
    if current_user:
        preferences = preferences_service.get_preferences(current_user.id)
        recipes_before = len(recipes)
        recipes = RecipeFilterService.filter_recipes(recipes, preferences)
        logger.info(
            f"Filtered search results: {recipes_before} -> {len(recipes)} "
            f"for user {current_user.id}"
        )

    # Convert to summaries for response
    recipe_summaries = [
        RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            thumbnail=recipe.thumbnail or "",
        )
        for recipe in recipes
    ]

    return RecipeListResponse(recipes=recipe_summaries)


@router.get("/random", response_model=RecipeDetailResponse)
async def get_random_recipe(
    current_user: UserResponse | None = Depends(get_optional_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
):
    """Get a random recipe.

    If user is authenticated, retries up to MAX_RANDOM_ATTEMPTS times
    to find a compatible recipe.
    """
    # If not authenticated, return first random recipe
    if not current_user:
        response = await themealdb_client.get_random()
        meals = response.get("meals") or []
        if not meals:
            return RecipeDetailResponse(recipe=None)
        recipe = Recipe.from_api_response(meals[0])
        return RecipeDetailResponse(recipe=recipe)

    # Authenticated user: apply filtering with retry logic
    preferences = preferences_service.get_preferences(current_user.id)

    for attempt in range(MAX_RANDOM_ATTEMPTS):
        response = await themealdb_client.get_random()
        meals = response.get("meals") or []

        if not meals:
            continue

        recipe = Recipe.from_api_response(meals[0])
        filtered = RecipeFilterService.filter_recipes([recipe], preferences)

        if filtered:
            logger.info(
                f"Found compatible random recipe after {attempt + 1} attempts "
                f"for user {current_user.id}"
            )
            return RecipeDetailResponse(recipe=filtered[0])

    # No compatible recipe found after max attempts
    logger.warning(
        f"No compatible random recipe found after {MAX_RANDOM_ATTEMPTS} attempts "
        f"for user {current_user.id}"
    )
    return RecipeDetailResponse(recipe=None)


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
async def get_recipes_by_category(
    category_name: str,
    current_user: UserResponse | None = Depends(get_optional_user),
    preferences_service: PreferencesService = Depends(get_preferences_service),
):
    """Get recipes by category.

    If user is authenticated, filters results based on their preferences.
    Note: Category endpoint only returns summaries, so we fetch full details
    for each recipe to enable proper filtering.
    """
    response = await themealdb_client.filter_by_category(category_name)
    meals = response.get("meals") or []

    # If not authenticated, return summaries directly
    if not current_user:
        recipes = [
            RecipeSummary(
                id=meal["idMeal"],
                name=meal["strMeal"],
                thumbnail=meal["strMealThumb"],
            )
            for meal in meals
        ]
        return RecipeListResponse(recipes=recipes)

    # Authenticated user: fetch full recipes for filtering
    preferences = preferences_service.get_preferences(current_user.id)
    full_recipes: list[Recipe] = []

    for meal in meals:
        detail_response = await themealdb_client.get_by_id(meal["idMeal"])
        detail_meals = detail_response.get("meals") or []
        if detail_meals:
            full_recipes.append(Recipe.from_api_response(detail_meals[0]))

    # Apply filtering
    recipes_before = len(full_recipes)
    filtered_recipes = RecipeFilterService.filter_recipes(full_recipes, preferences)
    logger.info(
        f"Filtered category '{category_name}' results: {recipes_before} -> "
        f"{len(filtered_recipes)} for user {current_user.id}"
    )

    # Convert to summaries for response
    recipe_summaries = [
        RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            thumbnail=recipe.thumbnail or "",
        )
        for recipe in filtered_recipes
    ]

    return RecipeListResponse(recipes=recipe_summaries)


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe_by_id(recipe_id: str):
    """Get recipe details by ID."""
    response = await themealdb_client.get_by_id(recipe_id)
    meals = response.get("meals") or []

    if not meals:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = Recipe.from_api_response(meals[0])
    return RecipeDetailResponse(recipe=recipe)
