#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, Pizza, RestaurantPizza
import os
from flask_cors import CORS

# Setup the app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
cors = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


# Routes
@app.route("/")
def index():
    return "<h1>Welcome to the Pizza API</h1>"


# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # Manually convert restaurants to dict and exclude 'restaurant_pizzas'
    return jsonify([{
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } for restaurant in restaurants]), 200

# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    # Manually include the 'restaurant_pizzas' field in the response
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [restaurant_pizza.to_dict() for restaurant_pizza in restaurant.restaurant_pizzas]
    }), 200



# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(exclude=["restaurant_pizzas"]) for pizza in pizzas]), 200



# Route: POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Validation of price
    if data.get("price") is None or not (1 <= data["price"] <= 30):
        return jsonify({"errors": ["validation errors"]}), 400  

    try:
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = restaurant_pizza.to_dict(
            only=("id", "price", "pizza", "pizza_id", "restaurant", "restaurant_id")
        )
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
