"""Shopping list service for generating and managing shopping lists."""

import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from app.models.shopping_list import (
    CategoryGroupResponse,
    IngredientCategory,
    ShoppingListGenerateResponse,
    ShoppingListItemResponse,
    ShoppingListResponse,
)
from app.services.meal_slots_service import MealSlotsService
from app.services.supabase import get_supabase_admin
from app.services.themealdb import themealdb_client

# Static ingredient to category mapping
# Maps common ingredient names (lowercase) to their category
INGREDIENT_CATEGORIES: dict[IngredientCategory, list[str]] = {
    IngredientCategory.LEGUMES: [
        # French
        "tomate",
        "tomates",
        "oignon",
        "oignons",
        "carotte",
        "carottes",
        "poivron",
        "poivrons",
        "courgette",
        "courgettes",
        "aubergine",
        "aubergines",
        "haricot",
        "haricots",
        "haricots verts",
        "salade",
        "laitue",
        "concombre",
        "concombres",
        "pomme de terre",
        "pommes de terre",
        "patate",
        "patates",
        "ail",
        "champignon",
        "champignons",
        "epinard",
        "epinards",
        "brocoli",
        "brocolis",
        "chou",
        "chou-fleur",
        "celeri",
        "poireau",
        "poireaux",
        "artichaut",
        "asperge",
        "asperges",
        "betterave",
        "navet",
        "radis",
        "fenouil",
        "endive",
        "mais",
        "petit pois",
        "petits pois",
        "avocat",
        "citron",
        "citrons",
        "lime",
        "gingembre",
        "echalote",
        "echalotes",
        "ciboulette",
        "persil",
        "coriandre",
        "basilic",
        "menthe",
        "thym",
        "romarin",
        "laurier",
        "aneth",
        "estragon",
        # English (TheMealDB uses English)
        "tomato",
        "tomatoes",
        "onion",
        "onions",
        "red onion",
        "red onions",
        "spring onion",
        "spring onions",
        "carrot",
        "carrots",
        "pepper",
        "peppers",
        "bell pepper",
        "red pepper",
        "green pepper",
        "zucchini",
        "courgette",
        "eggplant",
        "aubergine",
        "green beans",
        "lettuce",
        "cucumber",
        "potato",
        "potatoes",
        "garlic",
        "garlic clove",
        "garlic cloves",
        "mushroom",
        "mushrooms",
        "spinach",
        "broccoli",
        "cabbage",
        "cauliflower",
        "celery",
        "leek",
        "leeks",
        "artichoke",
        "asparagus",
        "beetroot",
        "turnip",
        "radish",
        "fennel",
        "corn",
        "sweetcorn",
        "peas",
        "avocado",
        "lemon",
        "lemon juice",
        "lime",
        "lime juice",
        "ginger",
        "shallot",
        "shallots",
        "chives",
        "parsley",
        "coriander",
        "cilantro",
        "basil",
        "mint",
        "thyme",
        "rosemary",
        "bay leaf",
        "bay leaves",
        "dill",
        "tarragon",
        "oregano",
        "sage",
        "chili",
        "chilli",
        "jalapeno",
        "kale",
        "bok choy",
        "water chestnuts",
        "bean sprouts",
        "bamboo shoots",
    ],
    IngredientCategory.VIANDES: [
        # French
        "poulet",
        "boeuf",
        "porc",
        "agneau",
        "veau",
        "canard",
        "dinde",
        "lapin",
        "saucisse",
        "saucisses",
        "bacon",
        "lardons",
        "jambon",
        "viande hachee",
        "steak",
        "cote",
        "cotes",
        "filet",
        "cuisse",
        "cuisses",
        "aile",
        "ailes",
        # English
        "chicken",
        "chicken breast",
        "chicken thigh",
        "chicken thighs",
        "chicken leg",
        "chicken legs",
        "chicken wing",
        "chicken wings",
        "beef",
        "beef mince",
        "ground beef",
        "minced beef",
        "steak",
        "beef steak",
        "pork",
        "pork chop",
        "pork chops",
        "pork loin",
        "lamb",
        "lamb chop",
        "lamb chops",
        "lamb mince",
        "ground lamb",
        "veal",
        "duck",
        "duck breast",
        "turkey",
        "turkey breast",
        "rabbit",
        "sausage",
        "sausages",
        "chorizo",
        "bacon",
        "pancetta",
        "ham",
        "prosciutto",
        "ground meat",
        "mince",
        "meatballs",
    ],
    IngredientCategory.POISSONS: [
        # French
        "saumon",
        "thon",
        "cabillaud",
        "morue",
        "crevette",
        "crevettes",
        "moule",
        "moules",
        "crabe",
        "homard",
        "sardine",
        "sardines",
        "maquereau",
        "truite",
        "sole",
        "bar",
        "dorade",
        "lotte",
        "anchois",
        "huitre",
        "huitres",
        "calamar",
        "calamars",
        "poulpe",
        "langoustine",
        "palourde",
        # English
        "salmon",
        "smoked salmon",
        "tuna",
        "cod",
        "shrimp",
        "shrimps",
        "prawn",
        "prawns",
        "king prawns",
        "mussel",
        "mussels",
        "crab",
        "lobster",
        "sardine",
        "sardines",
        "mackerel",
        "trout",
        "sole",
        "sea bass",
        "bream",
        "monkfish",
        "anchovy",
        "anchovies",
        "oyster",
        "oysters",
        "squid",
        "calamari",
        "octopus",
        "clam",
        "clams",
        "scallop",
        "scallops",
        "fish",
        "white fish",
        "fish sauce",
        "fish stock",
        "seafood",
        "haddock",
        "halibut",
        "tilapia",
    ],
    IngredientCategory.PRODUITS_LAITIERS: [
        # French
        "lait",
        "beurre",
        "creme",
        "creme fraiche",
        "creme liquide",
        "fromage",
        "yaourt",
        "yogourt",
        "oeuf",
        "oeufs",
        "mozzarella",
        "parmesan",
        "gruyere",
        "emmental",
        "camembert",
        "brie",
        "chevre",
        "roquefort",
        "ricotta",
        "mascarpone",
        "feta",
        "cheddar",
        # English
        "milk",
        "whole milk",
        "skimmed milk",
        "butter",
        "unsalted butter",
        "cream",
        "single cream",
        "double cream",
        "heavy cream",
        "whipping cream",
        "sour cream",
        "creme fraiche",
        "cheese",
        "cheddar cheese",
        "parmesan",
        "parmesan cheese",
        "mozzarella",
        "mozzarella cheese",
        "feta",
        "feta cheese",
        "ricotta",
        "mascarpone",
        "cream cheese",
        "cottage cheese",
        "goat cheese",
        "gruyere",
        "emmental",
        "brie",
        "yogurt",
        "yoghurt",
        "greek yogurt",
        "egg",
        "eggs",
        "egg yolk",
        "egg yolks",
        "egg white",
        "egg whites",
    ],
    IngredientCategory.EPICERIE: [
        # French
        "riz",
        "pates",
        "spaghetti",
        "tagliatelles",
        "penne",
        "lasagne",
        "lasagnes",
        "farine",
        "sucre",
        "sel",
        "poivre",
        "huile",
        "huile d'olive",
        "huile de tournesol",
        "vinaigre",
        "vinaigre balsamique",
        "moutarde",
        "sauce soja",
        "sauce tomate",
        "concentre de tomate",
        "tomates pelees",
        "miel",
        "sirop d'erable",
        "noix",
        "noisette",
        "noisettes",
        "amande",
        "amandes",
        "cacahuete",
        "cacahuetes",
        "noix de cajou",
        "pignon",
        "pignons",
        "sesame",
        "curry",
        "cumin",
        "paprika",
        "cannelle",
        "muscade",
        "curcuma",
        "coriandre moulue",
        "piment",
        "bouillon",
        "bouillon cube",
        "maizena",
        "levure",
        "bicarbonate",
        "vanille",
        "chocolat",
        "cacao",
        "confiture",
        "cornichon",
        "cornichons",
        "olive",
        "olives",
        "capre",
        "capres",
        "raisin sec",
        "raisins secs",
        "pois chiche",
        "pois chiches",
        "lentille",
        "lentilles",
        "haricot rouge",
        "haricots rouges",
        "haricot blanc",
        "haricots blancs",
        "noix de coco",
        "lait de coco",
        "tahini",
        "harissa",
        "ras el hanout",
        # English
        "rice",
        "basmati rice",
        "jasmine rice",
        "long grain rice",
        "arborio rice",
        "risotto rice",
        "pasta",
        "spaghetti",
        "penne",
        "tagliatelle",
        "fettuccine",
        "linguine",
        "macaroni",
        "noodles",
        "egg noodles",
        "rice noodles",
        "lasagne sheets",
        "flour",
        "plain flour",
        "self-raising flour",
        "bread flour",
        "cornflour",
        "sugar",
        "caster sugar",
        "brown sugar",
        "icing sugar",
        "salt",
        "sea salt",
        "pepper",
        "black pepper",
        "oil",
        "olive oil",
        "vegetable oil",
        "sunflower oil",
        "sesame oil",
        "coconut oil",
        "vinegar",
        "white wine vinegar",
        "red wine vinegar",
        "balsamic vinegar",
        "rice vinegar",
        "mustard",
        "dijon mustard",
        "wholegrain mustard",
        "english mustard",
        "soy sauce",
        "dark soy sauce",
        "light soy sauce",
        "tomato sauce",
        "tomato paste",
        "tomato puree",
        "passata",
        "chopped tomatoes",
        "canned tomatoes",
        "tinned tomatoes",
        "sun-dried tomatoes",
        "honey",
        "maple syrup",
        "golden syrup",
        "treacle",
        "walnut",
        "walnuts",
        "hazelnut",
        "hazelnuts",
        "almond",
        "almonds",
        "ground almonds",
        "peanut",
        "peanuts",
        "peanut butter",
        "cashew",
        "cashews",
        "cashew nuts",
        "pine nuts",
        "sesame seeds",
        "curry powder",
        "garam masala",
        "cumin",
        "ground cumin",
        "cumin seeds",
        "paprika",
        "smoked paprika",
        "cinnamon",
        "ground cinnamon",
        "nutmeg",
        "turmeric",
        "ground coriander",
        "chili powder",
        "chilli flakes",
        "cayenne pepper",
        "mixed spice",
        "allspice",
        "cloves",
        "cardamom",
        "star anise",
        "chinese five spice",
        "stock",
        "chicken stock",
        "beef stock",
        "vegetable stock",
        "stock cube",
        "cornstarch",
        "yeast",
        "baking powder",
        "baking soda",
        "bicarbonate of soda",
        "vanilla",
        "vanilla extract",
        "vanilla essence",
        "chocolate",
        "dark chocolate",
        "milk chocolate",
        "cocoa",
        "cocoa powder",
        "jam",
        "pickle",
        "pickles",
        "gherkin",
        "gherkins",
        "olive",
        "olives",
        "black olives",
        "capers",
        "raisins",
        "sultanas",
        "dried fruit",
        "chickpeas",
        "lentils",
        "red lentils",
        "green lentils",
        "kidney beans",
        "cannellini beans",
        "black beans",
        "butter beans",
        "baked beans",
        "coconut",
        "desiccated coconut",
        "coconut milk",
        "coconut cream",
        "tahini",
        "harissa",
        "worcestershire sauce",
        "tabasco",
        "hot sauce",
        "hoisin sauce",
        "oyster sauce",
        "teriyaki sauce",
        "sriracha",
        "ketchup",
        "mayonnaise",
        "bread",
        "breadcrumbs",
        "panko",
        "tortilla",
        "tortillas",
        "wrap",
        "wraps",
        "pitta",
        "pitta bread",
        "naan",
        "naan bread",
        "couscous",
        "bulgur",
        "quinoa",
        "oats",
        "rolled oats",
        "porridge oats",
    ],
    IngredientCategory.BOISSONS: [
        # French
        "eau",
        "vin",
        "vin blanc",
        "vin rouge",
        "biere",
        "cidre",
        "jus",
        "jus d'orange",
        "jus de pomme",
        "cafe",
        "the",
        "lait",
        # English
        "water",
        "wine",
        "white wine",
        "red wine",
        "beer",
        "cider",
        "juice",
        "orange juice",
        "apple juice",
        "lemon juice",
        "lime juice",
        "coffee",
        "tea",
        "milk",
        "brandy",
        "rum",
        "whiskey",
        "whisky",
        "vodka",
        "sherry",
        "marsala",
        "sake",
        "mirin",
    ],
    IngredientCategory.SURGELES: [
        # French
        "glace",
        "creme glacee",
        "petits pois surgeles",
        "legumes surgeles",
        "frites",
        "poisson surgele",
        # English
        "ice cream",
        "frozen peas",
        "frozen vegetables",
        "frozen spinach",
        "frozen berries",
        "french fries",
        "chips",
        "frozen fish",
        "frozen prawns",
        "frozen shrimp",
        "puff pastry",
        "filo pastry",
        "shortcrust pastry",
    ],
}


def _build_category_lookup() -> dict[str, IngredientCategory]:
    """Build a reverse lookup dict from ingredient name to category."""
    lookup: dict[str, IngredientCategory] = {}
    for category, ingredients in INGREDIENT_CATEGORIES.items():
        for ingredient in ingredients:
            lookup[ingredient.lower()] = category
    return lookup


# Build lookup dict at module load for performance
_CATEGORY_LOOKUP = _build_category_lookup()


class ShoppingListService:
    """Service for managing shopping lists."""

    def __init__(self) -> None:
        """Initialize the shopping list service."""
        self.client = get_supabase_admin()
        self.table = "shopping_list_items"
        self.meal_slots_service = MealSlotsService()

    def _get_monday_of_week(self, d: date) -> date:
        """Get the Monday of the week for a given date."""
        return d - timedelta(days=d.weekday())

    def _normalize_ingredient_name(self, name: str) -> str:
        """Normalize ingredient name for matching.

        Converts to lowercase and strips whitespace.

        Args:
            name: Raw ingredient name

        Returns:
            Normalized ingredient name
        """
        return name.strip().lower()

    def _parse_quantity(self, measure: str) -> tuple[float | None, str]:
        """Parse a quantity string into numeric value and unit.

        Handles formats like:
        - "2" -> (2.0, "")
        - "1.5" -> (1.5, "")
        - "1/2" -> (0.5, "")
        - "200g" -> (200.0, "g")
        - "2 cups" -> (2.0, "cups")
        - "1/2 cup" -> (0.5, "cup")

        Args:
            measure: The measure string from TheMealDB

        Returns:
            Tuple of (numeric_value or None, unit_string)
        """
        if not measure:
            return (None, "")

        measure = measure.strip()

        # Handle fractions like "1/2", "1/4", "3/4"
        fraction_match = re.match(r"^(\d+)/(\d+)\s*(.*)$", measure)
        if fraction_match:
            numerator = float(fraction_match.group(1))
            denominator = float(fraction_match.group(2))
            if denominator != 0:
                value = numerator / denominator
                unit = fraction_match.group(3).strip()
                return (value, unit)

        # Handle mixed numbers like "1 1/2"
        mixed_match = re.match(r"^(\d+)\s+(\d+)/(\d+)\s*(.*)$", measure)
        if mixed_match:
            whole = float(mixed_match.group(1))
            numerator = float(mixed_match.group(2))
            denominator = float(mixed_match.group(3))
            if denominator != 0:
                value = whole + (numerator / denominator)
                unit = mixed_match.group(4).strip()
                return (value, unit)

        # Handle decimals with optional unit like "1.5", "200g", "2 cups"
        decimal_match = re.match(r"^(\d+(?:\.\d+)?)\s*(.*)$", measure)
        if decimal_match:
            value = float(decimal_match.group(1))
            unit = decimal_match.group(2).strip()
            return (value, unit)

        # Cannot parse - return as unit only
        return (None, measure)

    def _can_sum_quantities(
        self, q1: tuple[float | None, str], q2: tuple[float | None, str]
    ) -> bool:
        """Check if two quantities can be summed.

        Quantities can be summed if:
        - Both have numeric values
        - Both have the same unit (or both are unitless)

        Args:
            q1: First parsed quantity (value, unit)
            q2: Second parsed quantity (value, unit)

        Returns:
            True if quantities can be summed
        """
        if q1[0] is None or q2[0] is None:
            return False

        # Normalize units for comparison
        unit1 = q1[1].lower().rstrip("s")  # cups -> cup
        unit2 = q2[1].lower().rstrip("s")

        return unit1 == unit2

    def _format_quantity(self, value: float, unit: str) -> str:
        """Format a quantity value and unit into a string.

        Args:
            value: Numeric value
            unit: Unit string

        Returns:
            Formatted quantity string
        """
        # Format value: use integer if whole number, else 1 decimal
        if value == int(value):
            value_str = str(int(value))
        else:
            value_str = f"{value:.1f}"

        if unit:
            return f"{value_str} {unit}"
        return value_str

    def _sum_quantities(self, quantities: list[str]) -> str:
        """Sum a list of quantity strings if possible.

        If all quantities have the same unit, sums them.
        Otherwise, concatenates them with commas.

        Args:
            quantities: List of quantity strings

        Returns:
            Summed or concatenated quantity string
        """
        if not quantities:
            return ""

        if len(quantities) == 1:
            return quantities[0]

        parsed = [self._parse_quantity(q) for q in quantities]

        # Check if all can be summed
        first = parsed[0]
        can_sum = all(self._can_sum_quantities(first, p) for p in parsed[1:])

        if can_sum and first[0] is not None:
            total = sum(p[0] for p in parsed if p[0] is not None)
            # Use unit from first quantity (original case)
            _, original_unit = self._parse_quantity(quantities[0])
            return self._format_quantity(total, original_unit)

        # Cannot sum - concatenate
        return ", ".join(quantities)

    def _multiply_quantity(self, measure: str, portions: int) -> str:
        """Multiply a quantity by the number of portions.

        Args:
            measure: Original measure string
            portions: Number of portions to multiply by

        Returns:
            Multiplied quantity string
        """
        if portions <= 1:
            return measure

        value, unit = self._parse_quantity(measure)

        if value is not None:
            return self._format_quantity(value * portions, unit)

        # Cannot parse - return original
        return measure

    def _extract_ingredients_from_meal(
        self, meal_data: dict[str, Any]
    ) -> list[tuple[str, str]]:
        """Extract ingredient and measure pairs from TheMealDB response.

        TheMealDB returns ingredients as strIngredient1-20 and strMeasure1-20.

        Args:
            meal_data: Single meal data from TheMealDB

        Returns:
            List of (ingredient_name, measure) tuples
        """
        ingredients: list[tuple[str, str]] = []

        for i in range(1, 21):
            ingredient = meal_data.get(f"strIngredient{i}")
            measure = meal_data.get(f"strMeasure{i}")

            # Skip empty or None ingredients
            if not ingredient or not ingredient.strip():
                continue

            ingredient = ingredient.strip()
            measure = measure.strip() if measure else ""

            ingredients.append((ingredient, measure))

        return ingredients

    def _get_category(self, ingredient_name: str) -> IngredientCategory:
        """Get the category for an ingredient.

        Uses exact match first, then substring matching.
        Defaults to AUTRES if no match found.

        Args:
            ingredient_name: The ingredient name to categorize

        Returns:
            The IngredientCategory for this ingredient
        """
        normalized = self._normalize_ingredient_name(ingredient_name)

        # Try exact match first
        if normalized in _CATEGORY_LOOKUP:
            return _CATEGORY_LOOKUP[normalized]

        # Try substring matching for compound ingredients
        # e.g., "chicken breast" contains "chicken"
        for key, category in _CATEGORY_LOOKUP.items():
            if key in normalized or normalized in key:
                return category

        # Default to AUTRES
        return IngredientCategory.AUTRES

    async def generate_list(
        self, user_id: str, week_start: date
    ) -> ShoppingListGenerateResponse:
        """Generate a shopping list from the week's meal slots.

        Fetches all meal slots for the week, retrieves recipe details,
        extracts and aggregates ingredients, and saves to database.

        Args:
            user_id: The user's UUID
            week_start: Monday of the week

        Returns:
            Generated shopping list response
        """
        # First, delete existing items for this week
        self.delete_list(user_id, week_start)

        # Get week's meal slots
        slots = self.meal_slots_service.get_week_slots(user_id, week_start)

        if not slots:
            return ShoppingListGenerateResponse(
                items=[],
                week_start=week_start,
                generated_at=datetime.now(UTC),
            )

        # Aggregate ingredients: {normalized_name: {quantities: [], category}}
        aggregated: dict[str, dict[str, Any]] = {}

        for slot in slots:
            # Fetch recipe details from TheMealDB
            meal_response = await themealdb_client.get_by_id(slot.recipe_id)

            if not meal_response or not meal_response.get("meals"):
                continue

            meal_data = meal_response["meals"][0]
            ingredients = self._extract_ingredients_from_meal(meal_data)

            for ingredient_name, measure in ingredients:
                normalized = self._normalize_ingredient_name(ingredient_name)

                # Multiply by portions
                adjusted_measure = self._multiply_quantity(measure, slot.portions)

                if normalized not in aggregated:
                    aggregated[normalized] = {
                        "original_name": ingredient_name,
                        "quantities": [],
                        "category": self._get_category(ingredient_name),
                    }

                aggregated[normalized]["quantities"].append(adjusted_measure)

        # Build items list
        items_to_insert = []
        for normalized, data in aggregated.items():
            quantity = self._sum_quantities(data["quantities"])

            items_to_insert.append(
                {
                    "user_id": user_id,
                    "ingredient_name": data["original_name"],
                    "quantity": quantity if quantity else "1",
                    "category": data["category"].value,
                    "is_checked": False,
                    "week_start": week_start.isoformat(),
                }
            )

        # Insert items
        if items_to_insert:
            response = self.client.table(self.table).insert(items_to_insert).execute()
            inserted_data = response.data
        else:
            inserted_data = []

        # Build response
        items = [
            ShoppingListItemResponse(
                id=str(row["id"]),
                user_id=row["user_id"],
                ingredient_name=row["ingredient_name"],
                quantity=row["quantity"],
                category=IngredientCategory(row["category"]),
                is_checked=row["is_checked"],
                week_start=row["week_start"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in inserted_data
        ]

        # Sort by category then alphabetically
        items.sort(key=lambda x: (x.category.value, x.ingredient_name.lower()))

        return ShoppingListGenerateResponse(
            items=items,
            week_start=week_start,
            generated_at=datetime.now(UTC),
        )

    def get_list(self, user_id: str, week_start: date) -> ShoppingListResponse:
        """Get shopping list for a week.

        Args:
            user_id: The user's UUID
            week_start: Monday of the week

        Returns:
            Shopping list grouped by category
        """
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("week_start", week_start.isoformat())
            .order("category")
            .order("ingredient_name")
            .execute()
        )

        items = [
            ShoppingListItemResponse(
                id=str(row["id"]),
                user_id=row["user_id"],
                ingredient_name=row["ingredient_name"],
                quantity=row["quantity"],
                category=IngredientCategory(row["category"]),
                is_checked=row["is_checked"],
                week_start=row["week_start"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in response.data
        ]

        # Group by category
        categories_dict: dict[IngredientCategory, list[ShoppingListItemResponse]] = {}
        for item in items:
            if item.category not in categories_dict:
                categories_dict[item.category] = []
            categories_dict[item.category].append(item)

        # Build category groups in defined order
        category_order = [
            IngredientCategory.LEGUMES,
            IngredientCategory.VIANDES,
            IngredientCategory.POISSONS,
            IngredientCategory.PRODUITS_LAITIERS,
            IngredientCategory.EPICERIE,
            IngredientCategory.BOISSONS,
            IngredientCategory.SURGELES,
            IngredientCategory.AUTRES,
        ]

        categories = []
        for cat in category_order:
            if cat in categories_dict:
                cat_items = categories_dict[cat]
                categories.append(
                    CategoryGroupResponse(
                        category=cat,
                        items=cat_items,
                        item_count=len(cat_items),
                    )
                )

        total_items = len(items)
        checked_count = sum(1 for item in items if item.is_checked)

        return ShoppingListResponse(
            categories=categories,
            week_start=week_start,
            total_items=total_items,
            checked_count=checked_count,
        )

    def toggle_item(
        self, user_id: str, item_id: str
    ) -> ShoppingListItemResponse | None:
        """Toggle the checked state of an item.

        Args:
            user_id: The user's UUID
            item_id: The item's UUID

        Returns:
            Updated item or None if not found
        """
        # First, get the current item
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("id", item_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            return None

        current_item = response.data[0]
        new_checked_state = not current_item["is_checked"]

        # Update the item
        update_response = (
            self.client.table(self.table)
            .update({"is_checked": new_checked_state})
            .eq("id", item_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not update_response.data:
            return None

        row = update_response.data[0]
        return ShoppingListItemResponse(
            id=str(row["id"]),
            user_id=row["user_id"],
            ingredient_name=row["ingredient_name"],
            quantity=row["quantity"],
            category=IngredientCategory(row["category"]),
            is_checked=row["is_checked"],
            week_start=row["week_start"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def uncheck_all(self, user_id: str, week_start: date) -> int:
        """Uncheck all items for a week.

        Args:
            user_id: The user's UUID
            week_start: Monday of the week

        Returns:
            Number of items unchecked
        """
        # Get count of checked items first
        count_response = (
            self.client.table(self.table)
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("week_start", week_start.isoformat())
            .eq("is_checked", True)
            .execute()
        )

        count = count_response.count or 0

        if count > 0:
            # Update all checked items to unchecked
            self.client.table(self.table).update({"is_checked": False}).eq(
                "user_id", user_id
            ).eq("week_start", week_start.isoformat()).eq("is_checked", True).execute()

        return count

    def delete_list(self, user_id: str, week_start: date) -> int:
        """Delete all items for a week.

        Args:
            user_id: The user's UUID
            week_start: Monday of the week

        Returns:
            Number of items deleted
        """
        # Get count first
        count_response = (
            self.client.table(self.table)
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("week_start", week_start.isoformat())
            .execute()
        )

        count = count_response.count or 0

        if count > 0:
            self.client.table(self.table).delete().eq("user_id", user_id).eq(
                "week_start", week_start.isoformat()
            ).execute()

        return count
