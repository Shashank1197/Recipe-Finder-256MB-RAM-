import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Data lists
INGREDIENTS = [
    {"name": "Pasta", "category": "Pantry"},
    {"name": "Tomato Sauce", "category": "Pantry"},
    {"name": "Basil", "category": "Produce"},
    {"name": "Garlic", "category": "Produce"},
    {"name": "Chicken Breast", "category": "Meat"},
    {"name": "Soy Sauce", "category": "Pantry"},
    {"name": "Ginger", "category": "Produce"},
    {"name": "Rice", "category": "Pantry"},
    {"name": "Broccoli", "category": "Produce"},
    {"name": "Tortillas", "category": "Pantry"},
    {"name": "Cheddar Cheese", "category": "Dairy"},
    {"name": "Black Beans", "category": "Pantry"},
    {"name": "Avocado", "category": "Produce"},
    {"name": "Lime Juice", "category": "Produce"},
    {"name": "Olive Oil", "category": "Pantry"},
    {"name": "Parmesan Cheese", "category": "Dairy"},
    {"name": "Beef Steak", "category": "Meat"},
    {"name": "Bell Pepper", "category": "Produce"},
    {"name": "Onion", "category": "Produce"},
    {"name": "Lemon Juice", "category": "Produce"},
    {"name": "Egg", "category": "Dairy"},
    {"name": "Spinach", "category": "Produce"},
    {"name": "Mushrooms", "category": "Produce"},
    {"name": "Tofu", "category": "Produce"},
    {"name": "Sesame Oil", "category": "Pantry"},
    {"name": "Chili Powder", "category": "Pantry"},
    {"name": "Cumin", "category": "Pantry"},
    {"name": "Shrimp", "category": "Seafood"},
    {"name": "Quinoa", "category": "Pantry"},
    {"name": "Sweet Potato", "category": "Produce"},
    {"name": "Greek Yogurt", "category": "Dairy"},
    {"name": "Honey", "category": "Pantry"},
]

DIETARY_TAGS = [
    {"name": "Vegan"},
    {"name": "Vegetarian"},
    {"name": "Gluten-Free"},
    {"name": "Keto"},
    {"name": "High-Protein"},
    {"name": "Seafood"},
]

RECIPES = [
    {
        "title": "Classic Tomato Pasta",
        "instructions": "Boil pasta. Sauté minced garlic in olive oil, add tomato sauce and simmer. Toss in cooked pasta and garnish with fresh basil.",
        "prep_time": 15,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Pasta", "quantity": "200g"},
            {"name": "Tomato Sauce", "quantity": "1 cup"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Basil", "quantity": "5 leaves"},
            {"name": "Olive Oil", "quantity": "1 tbsp"}
        ],
        "tags": ["Vegan", "Vegetarian"]
    },
    {
        "title": "Chicken Stir-Fry",
        "instructions": "Sauté sliced chicken breast in sesame oil with minced ginger and garlic. Add broccoli florets and soy sauce. Cook until chicken is done.",
        "prep_time": 20,
        "difficulty": "Medium",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "300g"},
            {"name": "Soy Sauce", "quantity": "2 tbsp"},
            {"name": "Ginger", "quantity": "1 tsp"},
            {"name": "Broccoli", "quantity": "1 cup"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Sesame Oil", "quantity": "1 tbsp"}
        ],
        "tags": ["High-Protein"]
    },
    {
        "title": "Black Bean Quesadilla",
        "instructions": "Place cheese and black beans on a tortilla, fold in half. Cook on a skillet until golden brown and cheese is melted. Serve with avocado.",
        "prep_time": 10,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Tortillas", "quantity": "2"},
            {"name": "Cheddar Cheese", "quantity": "1/2 cup"},
            {"name": "Black Beans", "quantity": "1/2 cup"},
            {"name": "Avocado", "quantity": "1/2"},
            {"name": "Onion", "quantity": "1/4 cup"}
        ],
        "tags": ["Vegetarian"]
    },
    {
        "title": "Guacamole & Chips",
        "instructions": "Mash avocados with lime juice, minced onion, minced garlic, and a pinch of salt. Serve with tortilla chips.",
        "prep_time": 10,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Avocado", "quantity": "2"},
            {"name": "Lime Juice", "quantity": "1 tbsp"},
            {"name": "Garlic", "quantity": "1 clove"},
            {"name": "Onion", "quantity": "1/4 cup"},
            {"name": "Tortillas", "quantity": "4"} # Used to make chips
        ],
        "tags": ["Vegan", "Vegetarian", "Gluten-Free", "Keto"]
    },
    {
        "title": "Garlic Parmesan Chicken",
        "instructions": "Coat chicken breast with olive oil, minced garlic, and parmesan cheese. Bake at 400°F for 25 minutes. Garnish with fresh basil.",
        "prep_time": 30,
        "difficulty": "Medium",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "2 pieces"},
            {"name": "Garlic", "quantity": "3 cloves"},
            {"name": "Parmesan Cheese", "quantity": "1/4 cup"},
            {"name": "Olive Oil", "quantity": "2 tbsp"},
            {"name": "Basil", "quantity": "4 leaves"}
        ],
        "tags": ["High-Protein", "Keto"]
    },
    {
        "title": "Beef Fajitas",
        "instructions": "Sauté sliced beef steak, bell pepper, and onions in olive oil. Drizzle with lime juice and wrap in warm tortillas.",
        "prep_time": 20,
        "difficulty": "Medium",
        "ingredients": [
            {"name": "Beef Steak", "quantity": "300g"},
            {"name": "Bell Pepper", "quantity": "1"},
            {"name": "Onion", "quantity": "1"},
            {"name": "Tortillas", "quantity": "4"},
            {"name": "Lime Juice", "quantity": "1 tbsp"},
            {"name": "Olive Oil", "quantity": "1 tbsp"}
        ],
        "tags": ["High-Protein"]
    },
    {
        "title": "Tofu Veggie Stir-Fry",
        "instructions": "Sauté cubed tofu in sesame oil. Add broccoli, ginger, and garlic. Pour soy sauce and cook until vegetables are tender.",
        "prep_time": 20,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Tofu", "quantity": "250g"},
            {"name": "Broccoli", "quantity": "1 cup"},
            {"name": "Ginger", "quantity": "1 tsp"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Soy Sauce", "quantity": "2 tbsp"},
            {"name": "Sesame Oil", "quantity": "1 tbsp"}
        ],
        "tags": ["Vegan", "Vegetarian", "Gluten-Free"]
    },
    {
        "title": "Egg Scramble with Spinach",
        "instructions": "Beat eggs. Cook spinach in olive oil until wilted, add eggs and scramble. Stir in cheddar cheese.",
        "prep_time": 10,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Egg", "quantity": "3"},
            {"name": "Spinach", "quantity": "1 cup"},
            {"name": "Cheddar Cheese", "quantity": "1/4 cup"},
            {"name": "Olive Oil", "quantity": "1 tsp"}
        ],
        "tags": ["Vegetarian", "Keto", "Gluten-Free"]
    },
    {
        "title": "Shrimp Fried Rice",
        "instructions": "Sauté shrimp, onion, ginger, and garlic. Add cooked rice, egg scramble, and soy sauce, stir-fry until combined.",
        "prep_time": 15,
        "difficulty": "Medium",
        "ingredients": [
            {"name": "Shrimp", "quantity": "150g"},
            {"name": "Rice", "quantity": "2 cups"},
            {"name": "Soy Sauce", "quantity": "1.5 tbsp"},
            {"name": "Ginger", "quantity": "1 tsp"},
            {"name": "Garlic", "quantity": "1 clove"},
            {"name": "Egg", "quantity": "1"},
            {"name": "Onion", "quantity": "1/2 cup"}
        ],
        "tags": ["Seafood"]
    },
    {
        "title": "Quinoa Power Bowl",
        "instructions": "Bake cubed sweet potato. Combine cooked quinoa, sweet potato, black beans, and avocado. Drizzle with olive oil and lemon juice.",
        "prep_time": 25,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Quinoa", "quantity": "1 cup cooked"},
            {"name": "Sweet Potato", "quantity": "1 medium"},
            {"name": "Black Beans", "quantity": "1/2 cup"},
            {"name": "Avocado", "quantity": "1/2"},
            {"name": "Olive Oil", "quantity": "1 tbsp"},
            {"name": "Lemon Juice", "quantity": "1 tsp"}
        ],
        "tags": ["Vegan", "Vegetarian", "Gluten-Free"]
    },
    {
        "title": "Creamy Honey Yogurt",
        "instructions": "Mix greek yogurt with honey and a splash of lemon juice. Serve cold.",
        "prep_time": 5,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Greek Yogurt", "quantity": "1 cup"},
            {"name": "Honey", "quantity": "1 tbsp"},
            {"name": "Lemon Juice", "quantity": "1/2 tsp"}
        ],
        "tags": ["Vegetarian", "Gluten-Free"]
    },
    {
        "title": "Garlic Mushrooms",
        "instructions": "Sauté sliced mushrooms in olive oil with minced garlic until soft. Sprinkle with parmesan cheese.",
        "prep_time": 10,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Mushrooms", "quantity": "200g"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Olive Oil", "quantity": "1 tbsp"},
            {"name": "Parmesan Cheese", "quantity": "2 tbsp"}
        ],
        "tags": ["Vegetarian", "Keto", "Gluten-Free"]
    },
    {
        "title": "Sweet Potato Fries",
        "instructions": "Cut sweet potato into wedges. Toss with olive oil and garlic powder. Roast at 420°F for 20 minutes.",
        "prep_time": 25,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Sweet Potato", "quantity": "2 medium"},
            {"name": "Olive Oil", "quantity": "2 tbsp"},
            {"name": "Garlic", "quantity": "1 clove"}
        ],
        "tags": ["Vegan", "Vegetarian", "Gluten-Free"]
    },
    {
        "title": "Beef and Broccoli",
        "instructions": "Thinly slice beef. Stir-fry beef in sesame oil with ginger and garlic. Add broccoli and soy sauce. Cook until beef is tender.",
        "prep_time": 20,
        "difficulty": "Medium",
        "ingredients": [
            {"name": "Beef Steak", "quantity": "250g"},
            {"name": "Broccoli", "quantity": "1.5 cups"},
            {"name": "Soy Sauce", "quantity": "2 tbsp"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Ginger", "quantity": "1 tsp"},
            {"name": "Sesame Oil", "quantity": "1 tbsp"}
        ],
        "tags": ["Keto", "High-Protein"]
    },
    {
        "title": "Spinach Pasta",
        "instructions": "Boil pasta. Sauté garlic and spinach in olive oil. Toss pasta with sautéed spinach, olive oil, and parmesan cheese.",
        "prep_time": 15,
        "difficulty": "Easy",
        "ingredients": [
            {"name": "Pasta", "quantity": "200g"},
            {"name": "Spinach", "quantity": "2 cups"},
            {"name": "Garlic", "quantity": "2 cloves"},
            {"name": "Olive Oil", "quantity": "2 tbsp"},
            {"name": "Parmesan Cheese", "quantity": "3 tbsp"},
            {"name": "Basil", "quantity": "3 leaves"}
        ],
        "tags": ["Vegetarian"]
    }
]

SUBSTITUTIONS = [
    ("Lemon Juice", "Lime Juice"),
    ("Cheddar Cheese", "Parmesan Cheese"),
    ("Chicken Breast", "Tofu"),
    ("Spinach", "Broccoli"),
    ("Sweet Potato", "Mushrooms")
]

def seed_database():
    uri = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("COGNODB_USERNAME") or os.getenv("NEO4J_USERNAME", "cognodb")
    password = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD", "password")

    print(f"Connecting to CognoDB at {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to CognoDB database: {e}")
        return


    with driver.session() as session:
        # 1. Clear existing database for a clean start (Optional, but useful for seed testing)
        print("Clearing existing data...")
        session.run("MATCH (n) DETACH DELETE n")

        # 2. Constraints (IF NOT EXISTS in Neo4j 4/5)
        # Note: We merge nodes to avoid issues if constraints are already present.

        # 3. Create Ingredients
        print(f"Seeding {len(INGREDIENTS)} ingredients...")
        for ing in INGREDIENTS:
            session.run(
                "MERGE (i:Ingredient {name: $name}) ON CREATE SET i.category = $category",
                name=ing["name"],
                category=ing["category"]
            )

        # 4. Create Dietary Tags
        print(f"Seeding {len(DIETARY_TAGS)} dietary tags...")
        for tag in DIETARY_TAGS:
            session.run(
                "MERGE (t:DietaryTag {name: $name})",
                name=tag["name"]
            )

        # 5. Create Recipes and Relationships
        print(f"Seeding {len(RECIPES)} recipes and their relations...")
        for rec in RECIPES:
            # Create Recipe
            session.run(
                """
                MERGE (r:Recipe {title: $title})
                ON CREATE SET r.instructions = $instructions, 
                              r.prep_time = $prep_time, 
                              r.difficulty = $difficulty
                """,
                title=rec["title"],
                instructions=rec["instructions"],
                prep_time=rec["prep_time"],
                difficulty=rec["difficulty"]
            )

            # Create Recipe -> Ingredient (REQUIRES)
            for ing in rec["ingredients"]:
                session.run(
                    """
                    MATCH (r:Recipe {title: $recipe_title})
                    MATCH (i:Ingredient {name: $ingredient_name})
                    MERGE (r)-[:REQUIRES {quantity: $quantity}]->(i)
                    """,
                    recipe_title=rec["title"],
                    ingredient_name=ing["name"],
                    quantity=ing["quantity"]
                )

            # Create Recipe -> DietaryTag (HAS_TAG)
            for tag_name in rec["tags"]:
                session.run(
                    """
                    MATCH (r:Recipe {title: $recipe_title})
                    MATCH (t:DietaryTag {name: $tag_name})
                    MERGE (r)-[:HAS_TAG]->(t)
                    """,
                    recipe_title=rec["title"],
                    tag_name=tag_name
                )

        # 6. Create Ingredient Substitutions
        print(f"Seeding {len(SUBSTITUTIONS)} substitutions...")
        for ing1, ing2 in SUBSTITUTIONS:
            session.run(
                """
                MATCH (i1:Ingredient {name: $ing1})
                MATCH (i2:Ingredient {name: $ing2})
                MERGE (i1)-[:SUBSTITUTES]->(i2)
                """,
                ing1=ing1,
                ing2=ing2
            )

    driver.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
