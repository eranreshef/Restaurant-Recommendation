import json
from datetime import datetime
import boto3
import os
import logging
from boto3.dynamodb.conditions import Attr

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('RESTAURANT_TABLE', 'Restaurants')
table = dynamodb.Table(table_name)

def is_open(open_hour, close_hour, now):
    open_time = datetime.strptime(open_hour, '%H:%M').time()
    close_time = datetime.strptime(close_hour, '%H:%M').time()
    return open_time <= now.time() <= close_time


def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    query_params = event.get('queryStringParameters') or {}
    style = query_params.get('style')
    vegetarian = query_params.get('vegetarian') == 'true'
    open_now = query_params.get('openNow') == 'true'
    now = datetime.now()
    logger.info(f"Parsed query params - style: {style}, vegetarian: {vegetarian}, openNow: {open_now}")

    filter_expression = None
    if style:
        filter_expression = Attr('style').eq(style)
    if vegetarian:
        veg_expr = Attr('vegetarian').eq(True)
        filter_expression = veg_expr if not filter_expression else filter_expression & veg_expr

    response = table.scan(FilterExpression=filter_expression) if filter_expression else table.scan()
    restaurants = response.get('Items', [])

    result = []
    for r in restaurants:
        if not is_open(r['openHour'], r['closeHour'], now):
            continue
        result.append(r)
        break

    logger.info(f"returning result {result}")

    if result:
        return {
            "statusCode": 200,
            "body": json.dumps({"restaurantRecommendation": result[0]}),
            "headers": {"Content-Type": "application/json"}
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"message": "No matching restaurant found"}),
        "headers": {"Content-Type": "application/json"}
    }