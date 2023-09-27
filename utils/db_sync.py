from dotenv import dotenv_values
from utils.db import MongoConnection

config = dotenv_values(".env")
import json
import time

mongo_client = MongoConnection.get_db()


###
# Sync categories to mongodb
# @param: categories
# @return: Success message or error message if any
###
def sync_categories_to_db(categories):

    mongo_client.db.categories.insert_many(categories)

    print({'msg': 'Categories synced successfully'})


###
# Sync data to mongodb
# @param: category
# @param: products
# @return: Success message or error message if any
###
def sync_data_to_db(category, products):

    start = time.time()

    category_id = category.get('id')
    category_name = category.get('name')

    for product in products:

        data = {
            'category_id': category_id,
            'sku': product.get('sku'),
            'name': product.get('name'),
            'images': product.get('images'),
            'salePrice': product.get('salePrice'),
            'digital': product.get('digital'),
            'description': product.get('description'),
            'customerReviewCount': product.get('customerReviewCount'),
            'shippingCost': product.get('shippingCost'),
        }
        # with open('products.json', 'a') as f:
        #     json.dump(data, f)

        mongo_client.db.products.insert_one(data)

    f = open("db__sync.log", "a")
    f.write("Data synced successfully for category_id: " +
            str(category_id) + "-" + str(category_name) + "\n")
    f.close()

    print({'msg': 'Data synced successfully', 'category_id': category_id,
          'category_name': category_name})
    
    end = time.time()
    print("Time to sync_db ", end - start) 
