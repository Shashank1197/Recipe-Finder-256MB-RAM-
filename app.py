from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Register application context teardown to close Neo4j driver
@app.teardown_appcontext
def shutdown_driver(exception=None):
    db.close_driver()      

@app.route('/')
def index():
    """
    Renders the main Recipe Finder landing page.
    """
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_recipes():
    """
    POST API to search recipes by ingredients.
    Accepts JSON body: { "ingredients": "chicken, rice, tomato" }
    Returns matching recipes and lists missing ingredients.
    """
    data = request.get_json() or {}
    ingredients_str = data.get("ingredients", "")
    
    # Split the ingredients by commas and strip whitespace
    ingredients_list = [ing.strip() for ing in ingredients_str.split(",") if ing.strip()]
    
    if not ingredients_list:
        return jsonify({
            "status": "success",
            "recipes": []
        })

    try:
        recipes = db.search_recipes_by_ingredients(ingredients_list)
        return jsonify({
            "status": "success",
            "recipes": recipes
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500

@app.route('/suggestions', methods=['GET'])
def ingredient_suggestions():
    """
    GET API to get autocompletion suggestions as the user types.
    Query parameter: /suggestions?q=ch
    """
    query_str = request.args.get("q", "")
    
    try:
        suggestions_list = db.get_ingredient_suggestions(query_str)
        return jsonify({
            "status": "success",
            "suggestions": suggestions_list
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unable to fetch suggestions: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    # Disable reloader if running in background tasks to avoid duplicate driver setups
    app.run(host="0.0.0.0", port=port, debug=True)
