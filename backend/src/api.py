import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES

'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    drinks = Drink.query.order_by(Drink.id).all()

    drinks_formatted = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_formatted
    })


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    drinks = Drink.query.order_by(Drink.id).all()

    drinks_formatted = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_formatted
    })


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    new_title = body['title']
    new_recipe_dict = body['recipe']

    drink = Drink(title=new_title, recipe=json.dumps(new_recipe_dict))
    drink.insert()

    return jsonify({
        'succes': True,
        'drinks': [drink.long()]
    })


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    if not drink_id:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    body = request.get_json()

    title_updated = body.get('title', None)
    recipe_updated_dict = body.get('recipe', None)

    if title_updated:
        drink.title = title_updated

    if recipe_updated_dict:
        drink.recipe = json.dumps(recipe_updated_dict)

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    if not drink_id:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink:
        drink.delete()
    else:
        abort(404)

    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(AuthError):
    return jsonify({
        'success': False,
        'error': AuthError.status_code,
        'message': AuthError.error
    }), 401
