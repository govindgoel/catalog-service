import requests
from dotenv import dotenv_values
from .constants import GET_CATEGORIES_API_URL, GET_PRODUCT_FROM_CATEGORY_API_URL, RESPONSE_LIMIT, DEFAULT_PAGE
from .db_sync import sync_data_to_db, sync_categories_to_db
import logging as logger

config = dotenv_values(".env")
X_API_KEY = URI = config.get('X_API_KEY')


###
# Fetch and Sync data to mongodb
# @param: None
# @return: None
###
def fetch_data():
    categories = get_categories()
    # sync_categories_to_db(categories)
    print('___Get Products___')
    for category in categories:
        logger.info('___Syncing data for category: ' +
                    category.get('name') + '___')
        print('___Syncing data for category: ' +
              category.get('name') + '___')
        re = get_category_products(category.get('id'))
        if re is not None:
            sync_data_to_db(category, re)
            print('___Data synced successfully___')

###
# Get all categories
# @return: list of categories or error message if any
###


def get_categories():
    new_response = True
    categories = []
    time = 0

    print('___Get Categories___')
    try:
        while new_response:
            response = requests.get(GET_CATEGORIES_API_URL, params={
                                    'page': DEFAULT_PAGE, 'limit': RESPONSE_LIMIT}, headers={'x-api-key': X_API_KEY})
            time = time + response.elapsed.total_seconds()
            if response.json().get('categories') != None:
                new_response = response.json().get('categories', [])
                categories.extend(new_response)
                page += 1
            else:
                new_response = False

        print("Time:", time)
        print({'msg': 'Categories fetched successfully'})
        return categories

    except Exception as e:
        return {'error': str(e), 'categories': [], 'msg': 'Error while fetching categories'}


###
# Get all products of a category
# @param: category_id
# @return: list of products or error message if any
###

def get_category_products(category_id):
    new_response = True
    products = []
    time = 0
    print('___Get Products___')
    try:
        while new_response:
            response = requests.get(GET_PRODUCT_FROM_CATEGORY_API_URL, params={
                                    'page': DEFAULT_PAGE, 'limit': RESPONSE_LIMIT, 'categoryID': category_id}, headers={'x-api-key': X_API_KEY})
            time = time + response.elapsed.total_seconds()
            if response.json().get('products') != None:
                new_response = response.json().get('products', [])
                products.extend(new_response)
                page += 1
            else:
                new_response = False

        print("Time:", time)
        print({'msg': 'Products fetched successfully'})
        return products

    except Exception as e:
        return {'error': str(e), 'products': [], 'msg': 'Error while fetching products'}
