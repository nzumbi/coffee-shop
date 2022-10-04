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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_all_available_drinks():
    all_available_drinks =  Drink.query.order_by(Drink.id).all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in all_available_drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_details_for_all_available_drinks(jwt):
    all_available_drinks = Drink.query.all()
    all_available_drink_detail =   [drink.long() for drink in all_available_drinks]

    return jsonify({
        'success': True,
        'drinks': all_available_drink_detail
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
    information_about_drink = request.get_json()

    if 'title' and 'recipe' not in information_about_drink:
        abort(422)

    title_of_new_drink = information_about_drink['title']
    recipe_info_in_json = json.dumps(information_about_drink['recipe'])

    new_drink = Drink(title=title_of_new_drink, recipe=recipe_info_in_json)

    new_drink.insert()

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def change_drink_information(jwt, id):
    existing_drink = Drink.query.get(id)

    if existing_drink is None:
        abort(404)

    additional_drink_information = request.get_json()

    if 'title' in additional_drink_information:
        existing_drink.title = additional_drink_information['title']

    if 'recipe' in additional_drink_information:
        existing_drink.recipe = json.dumps(additional_drink_information['recipe'])

    existing_drink.update()

    return jsonify({
        'success': True,
        'drinks': [existing_drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')

def remove_drink(jwt, id):
    available_drink= Drink.query.get(id)
    if not available_drink:
        abort(404)

    available_drink.delete()

    return jsonify({
        'success': True,
        'delete': available_drink.id

        }), 200



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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(400)
def returns_error_400_making_bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(401)
def returns_error_401(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }),401

@app.errorhandler(405)
def returns_error_405_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405

@app.errorhandler(500)
def returns_internal_server_error_500(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
     }), 500

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
def resource_not_available(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "page not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(error):
    error_response = jsonify(error.error)
    error_response.status_code = error.status_code

    return error_response