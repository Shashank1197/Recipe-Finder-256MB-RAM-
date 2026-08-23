# Fridge to Table - Intelligent Recipe Finder

A clean, production-ready, and well-structured **Recipe Finder** web application built with Python, Flask, and the Neo4j Graph Database. The application answers a common daily question: **"What can I cook with the ingredients I already have at home?"**

It allows users to search recipes using whatever ingredients they have in their fridge. To offer an optimized search experience, it traverses a **2-hop relationship** path in Neo4j to find recipes matching direct ingredients as well as interchangeable substitutions (e.g., swapping Lemon Juice for Lime Juice), all while listing which ingredients are missing.

---

## Why a Graph Database?

A relational database (SQL) is built on structured tables. Querying a relationship-rich model like Recipe Finder in SQL requires multiple complex `JOIN` tables and subqueries, particularly when addressing ingredient substitutions:
* **The SQL Join Hell:** Connecting `Recipes` $\rightarrow$ `RecipeIngredients` $\rightarrow$ `Ingredients` $\rightarrow$ `IngredientSubstitutions` requires multiple joins. Each additional relationship level (like matching substitutes of substitutes) exponentially slows down query execution and results in extremely verbose, unmaintainable SQL code.
* **The Graph Advantage:** In a graph database, relationships are native entities stored directly as physical pointers. Traversal is O(1) per node. Finding a recipe that requires an ingredient or its substitutes is a simple path traversal:
  ```cypher
  (r:Recipe)-[:REQUIRES]->(req:Ingredient)-[:SUBSTITUTES]-(sub:Ingredient)
  ```
  This query runs with millisecond performance regardless of database size, and substitutions can be traversed symmetrically and recursively with trivial Cypher syntax.

---

## Graph Data Model

The application leverages the following node types and relationship graph structure:

### Nodes
* `(:Recipe {title: String, instructions: String, prep_time: Integer, difficulty: String})`
* `(:Ingredient {name: String, category: String})`
* `(:DietaryTag {name: String})`

### Relationships
* `(Recipe)-[:REQUIRES {quantity: String}]->(Ingredient)`
* `(Recipe)-[:HAS_TAG]->(DietaryTag)`
* `(Ingredient)-[:SUBSTITUTES]->(Ingredient)` (Bidirectional traversal)

### Text Diagram
```text
                  [:HAS_TAG]
 (DietaryTag) <----------------- (Recipe)
                                    |
                                    | [:REQUIRES {quantity}]
                                    v
(Ingredient) <------------- (Ingredient)
              [:SUBSTITUTES]
```

---

## Project Structure

```text
/recipe-finder
│
├── app.py                  # Main Flask web server entry point
├── db.py                  # Neo4j connection lifecycle & Cypher queries
├── seed.py                 # Graph database data seeder script
├── .env.example            # Template for environment configuration
├── requirements.txt        # Python package dependencies
├── /templates
│   └── index.html          # Clean Bootstrap 5 and Javascript UI
└── /static
    └── style.css           # Custom dark glassmorphism styling
```

---

## Setup & Running Instructions

### 1. Prerequisites
* **Python 3.9+** installed.
* **Neo4j DBMS** running (local instance via Neo4j Desktop / Community Server or Neo4j Aura cloud instance).

### 2. Install Dependencies
Clone or navigate to the project directory, then run:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a file named `.env` in the root directory and specify your Neo4j connection credentials:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
PORT=5000
```
*(You can refer to `.env.example` as a template).*

### 4. Seed the Database
Run the standalone seeder script to populate your Neo4j instance with 15+ recipes, 30+ ingredients, substitutions, and tags:
```bash
python seed.py
```
This script uses `MERGE` statements and can be run multiple times safely without producing duplicate data.

### 5. Start the Application
Launch the Flask development server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to start searching!

---

## Application Screenshots

### Main Interface (Empty State)
*(Screenshot Placeholder - Glassmorphic Search Landing Page)*

### Search Results with Missing Ingredients
*(Screenshot Placeholder - Cards Grid displaying matched recipes, tags, difficulty, and missing items highlighted in red)*
