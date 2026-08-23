import os
from neo4j import GraphDatabase, exceptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_driver = None

def get_driver():
    """
    Get or initialize the global Neo4j driver instance.
    Includes connection error handling and validation.
    """
    global _driver
    if _driver is not None:
        return _driver

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    try:
        # Create driver instance with connection pool settings
        _driver = GraphDatabase.driver(uri, auth=(username, password))
        # Validate connection immediately
        _driver.verify_connectivity()
        return _driver
    except Exception as e:
        print(f"Error initializing Neo4j driver: {e}")
        _driver = None
        raise e

def close_driver():
    """
    Close the global Neo4j driver instance.
    """
    global _driver
    if _driver is not None:
        try:
            _driver.close()
        except Exception as e:
            print(f"Error closing Neo4j driver: {e}")
        finally:
            _driver = None

def get_ingredient_suggestions(query_str):
    """
    Query ingredient auto-completions based on user input.
    Case-insensitive match. Returns a list of ingredient names.
    """
    if not query_str or not query_str.strip():
        return []

    try:
        driver = get_driver()
        # Parameterized query to avoid Cypher injection
        query = """
        MATCH (i:Ingredient)
        WHERE toLower(i.name) CONTAINS toLower($query_str)
        RETURN i.name AS name
        ORDER BY i.name ASC
        LIMIT 10
        """
        with driver.session() as session:
            result = session.run(query, query_str=query_str.strip())
            return [record["name"] for record in result]
    except Exception as e:
        print(f"Database error in get_ingredient_suggestions: {e}")
        raise e

def search_recipes_by_ingredients(ingredients_list):
    """
    Find recipes that require all of the provided ingredients (or their substitutes).
    Returns list of matching recipes with tags, instructions, and missing ingredients.
    
    CRITICAL 2-HOP TRAVERSAL PATTERN:
    - Hop 1: (Recipe)-[:REQUIRES]->(Ingredient)
    - Hop 2: (Ingredient)-[:SUBSTITUTES]-(Ingredient)
    """
    if not ingredients_list:
        return []

    # Normalize ingredients: lower-case and strip spaces
    input_ingredients = [ing.strip().lower() for ing in ingredients_list if ing.strip()]
    if not input_ingredients:
        return []

    try:
        driver = get_driver()
        
        # Parameterized 2-hop query.
        # Finds recipes 'r' that require 'req' where 'req' matches the user's input 'sub'
        # either directly (req = sub) or through a SUBSTITUTES relationship (req - SUBSTITUTES - sub).
        query = """
        MATCH (sub:Ingredient)
        WHERE toLower(sub.name) IN $input_ingredients
        
        MATCH (r:Recipe)-[:REQUIRES]->(req:Ingredient)
        WHERE req = sub OR (req)-[:SUBSTITUTES]-(sub)
        
        WITH r, count(DISTINCT sub.name) AS match_count
        WHERE match_count = size($input_ingredients)
        
        MATCH (r)-[req_rel:REQUIRES]->(all_req:Ingredient)
        OPTIONAL MATCH (all_req)-[:SUBSTITUTES]-(sub_opt:Ingredient)
        OPTIONAL MATCH (r)-[:HAS_TAG]->(tag:DietaryTag)
        
        RETURN 
          r.title AS title,
          r.instructions AS instructions,
          r.prep_time AS prep_time,
          r.difficulty AS difficulty,
          tag.name AS tag_name,
          all_req.name AS req_name,
          all_req.category AS req_category,
          req_rel.quantity AS req_quantity,
          sub_opt.name AS sub_name
        """
        
        with driver.session() as session:
            result = session.run(query, input_ingredients=input_ingredients)
            
            recipes_map = {}
            for record in result:
                title = record["title"]
                if title not in recipes_map:
                    recipes_map[title] = {
                        "title": title,
                        "instructions": record["instructions"],
                        "prep_time": record["prep_time"],
                        "difficulty": record["difficulty"],
                        "tags": set(),
                        "ingredients": {}
                    }
                
                recipe = recipes_map[title]
                if record["tag_name"]:
                    recipe["tags"].add(record["tag_name"])
                
                req_name = record["req_name"]
                if req_name:
                    if req_name not in recipe["ingredients"]:
                        recipe["ingredients"][req_name] = {
                            "name": req_name,
                            "category": record["req_category"],
                            "quantity": record["req_quantity"],
                            "substitutes": set()
                        }
                    if record["sub_name"]:
                        recipe["ingredients"][req_name]["substitutes"].add(record["sub_name"])
            
            # Post-process results: compute missing ingredients
            recipes = []
            for recipe in recipes_map.values():
                missing = []
                for req_name, info in recipe["ingredients"].items():
                    req_name_lower = req_name.lower()
                    has_ingredient = (req_name_lower in input_ingredients)
                    
                    if not has_ingredient:
                        # Check substitutes
                        for sub in info["substitutes"]:
                            if sub.lower() in input_ingredients:
                                has_ingredient = True
                                break
                    
                    if not has_ingredient:
                        qty_str = f" ({info['quantity']})" if info['quantity'] else ""
                        missing.append(f"{req_name}{qty_str}")
                
                recipes.append({
                    "title": recipe["title"],
                    "instructions": recipe["instructions"],
                    "prep_time": recipe["prep_time"],
                    "difficulty": recipe["difficulty"],
                    "tags": sorted(list(recipe["tags"])),
                    "missing_ingredients": missing
                })
            
            # Sort by number of missing ingredients (recipes you can make easiest first)
            recipes.sort(key=lambda r: len(r["missing_ingredients"]))
            return recipes
            
    except Exception as e:
        print(f"Database error in search_recipes_by_ingredients: {e}")
        raise e
