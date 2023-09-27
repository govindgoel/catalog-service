from flask import Flask, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from utils.db import MongoConnection
from dotenv import dotenv_values
from flask import render_template


from utils.api import fetch_data
from utils.constants import RESPONSE_LIMIT, DEFAULT_PAGE

client = MongoConnection.get_db()

config = dotenv_values(".env")


app = Flask(__name__)

CORS(app)

###
# Token required decorator
# @param: function to be decorated
# @return: decorator
###


def token_required(f):
    def decorator(*args, **kwargs):
        token = None
        # ensure the access-token is passed with the headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            if token == config.get('X_API_KEY'):
                return f(*args, **kwargs)
        if not token:  # throw error if no token provided
            return ({"message": "Unoauthoirized Access"}, 401)
    decorator.__name__ = f.__name__
    return decorator


@app.route("/")
def home():
    pipeline = [
            {
                "$lookup": {
                    "from": "products",
                    "localField": "id",
                    "foreignField": "category_id",
                    "as": "products"
                }
            },
            {
                "$addFields": {
                    "productCount": {"$size": "$products"}
                }
            },
            {
                "$limit": 20
            },
            {
                "$sort": {"productCount": -1}
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "name": 1,
                }
            },
        ]

        # Execute the aggregation query
    result = list(client.db.categories.aggregate(pipeline))
    
    return render_template('index.html', categories=result, count=10)


@app.route("/products/<categoryID>")
def products(categoryID):
    products =  products = client.db.products.find({'category_id': categoryID}, {'_id': False,'category_id':False}).sort("customerReviewCount", -1).limit(int(20))
    return render_template('products.html', products=list(products))


###
# Fetch and Sync data to mongodb
# @param: None
# @return: Success or error message if any
###
@app.route('/syncData', methods=['POST'])
@token_required
def sync_to_database():
    try:
        fetch_data()
        return "Success"
    except Exception as e:
        return str(e)


###
# Get all categories
# @return: list of categories or error message if any
###

@app.route('/shop/categories', methods=['GET'])
@token_required
def get_categories():

    limit = request.args.get('limit') | RESPONSE_LIMIT
    page = request.args.get('page') | DEFAULT_PAGE

    if limit is None:
        limit = RESPONSE_LIMIT
    if page is None:
        page = DEFAULT_PAGE

    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "products",
                    "localField": "id",
                    "foreignField": "category_id",
                    "as": "products"
                }
            },
            {
                "$addFields": {
                    "productCount": {"$size": "$products"}
                }
            },
            {
                "$skip": (int(page)-1)*int(limit)
            },
            {
                "$limit": int(limit)
            },
            {
                "$sort": {"productCount": -1}
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "name": 1,
                }
            },
        ]

        # Execute the aggregation query
        result = list(client.db.categories.aggregate(pipeline))

        total_pages = int(client.db.categories.count_documents({})/int(limit))
        if total_pages == 0:
            total_pages = 1
        data = {'categories': list(result),
                'page': int(page), 'total_pages': total_pages}
        return data
    except Exception as e:
        return ({'error': str(e), 'categories': [], 'msg': 'Error while fetching categories'}, 404)


###
# Get all products
# @return: list of products or error message if any
###

@app.route('/shop/products', methods=['GET'])
@token_required
def get_products():
    limit = request.args.get('limit') | RESPONSE_LIMIT
    page = request.args.get('page') | DEFAULT_PAGE
    categoryId = request.args.get('categoryID')

    if categoryId is None:
        return ({'error': 'Category ID is required', 'products': []}, 404)

    if limit is None:
        limit = RESPONSE_LIMIT
    if page is None:
        page = DEFAULT_PAGE

    try:
        products = client.db.products.find({'category_id': categoryId}, {'_id': False,'category_id':False}).sort("customerReviewCount", -1).skip(
            (int(page)-1)*int(limit)).limit(int(limit))

        total_pages = int(client.db.products.count_documents(
            {'category_id': categoryId})/int(limit))
        if total_pages == 0:
            total_pages = 1
        data = {'categories': list(products),
                'page': int(page), 'total_pages': total_pages}
        return data
    except Exception as e:
        return ({'error': str(e), 'products': []}, 404)


if __name__ == "__main__":
  app.run(host='0.0.0.0')
