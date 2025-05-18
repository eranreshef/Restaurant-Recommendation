import json
import boto3
import logging
import os
from datetime import datetime
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import BotoCoreError, ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource and get table reference using an environment variable
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("RESTAURANT_TABLE")
table = dynamodb.Table(table_name)

# Supported restaurant styles for filtering
KNOWN_STYLES = {"italian", "french", "korean", "chinese", "indian", "mexican", "japanese", "vegan"}

def parse_sentence(sentence: str) -> dict:
    """
    Parses the user-provided sentence to extract filtering criteria.
    Example input: "Show me a vegetarian Italian place that offers delivery and is open now"
    """
    logger.info(f"Parsing sentence: '{sentence}'")
    sentence = sentence.lower()

    # Check for known styles and other keywords
    style = next((s for s in KNOWN_STYLES if s in sentence), None)
    vegetarian = "vegetarian" in sentence or "vegeterian" in sentence  # Handle typo
    deliveries = "delivery" in sentence or "delivers" in sentence
    open_now = "open now" in sentence or "currently open" in sentence

    parsed = {
        "style": style,
        "vegetarian": vegetarian,
        "deliveries": deliveries,
        "open_now": open_now
    }
    logger.info(f"Extracted filters from sentence: {parsed}")
    return parsed

def get_filtered_restaurants(style=None, vegetarian=None, deliveries=None):
    """
    Queries DynamoDB using optional filters for style, vegetarian, and deliveries.
    """
    logger.info("Building DynamoDB filter expression.")
    filter_expr = None

    # Build conditional expressions based on which filters are provided
    if style:
        filter_expr = Attr("style").eq(style)
        logger.info(f"Filter: style = '{style}'")
    if vegetarian:
        expr = Attr("vegetarian").eq(vegetarian)
        logger.info(f"Filter: vegetarian = {vegetarian}")
        filter_expr = expr if filter_expr is None else filter_expr & expr
    if deliveries:
        expr = Attr("deliveries").eq(deliveries)
        logger.info(f"Filter: deliveries = {deliveries}")
        filter_expr = expr if filter_expr is None else filter_expr & expr

    try:
        # Query the DynamoDB table with or without filters
        logger.info("Querying DynamoDB...")
        response = table.scan(FilterExpression=filter_expr) if filter_expr else table.scan()
        restaurants = response.get("Items", [])
        logger.info(f"Found {len(restaurants)} matching restaurant(s) from DynamoDB.")
        return restaurants

    except (BotoCoreError, ClientError) as e:
        # Handle AWS-related errors
        logger.error("DynamoDB service error — possibly unavailable", exc_info=True)
        raise RuntimeError("DynamoDB is unavailable") from e

    except Exception as e:
        # Handle any other unexpected errors
        logger.error("Unexpected error querying DynamoDB", exc_info=True)
        raise RuntimeError("Unexpected error accessing database") from e

def is_open(restaurant: dict) -> bool:
    """
    Determines whether a restaurant is currently open based on its opening and closing hours.
    Handles overnight closing hours (e.g., 22:00 to 02:00).
    """
    try:
        now = datetime.now().time()
        open_time = datetime.strptime(restaurant["openHour"], "%H:%M").time()
        close_time = datetime.strptime(restaurant["closeHour"], "%H:%M").time()

        # Determine if the current time falls within open and close range
        open_status = open_time <= now <= close_time if open_time < close_time else now >= open_time or now <= close_time
        logger.info(f"Checking if '{restaurant['name']}' is open now ({now}): {open_status}")
        return open_status
    except Exception as e:
        # If hours are not parseable or missing, assume closed
        logger.warning(f"Failed to parse open/close hours for '{restaurant.get('name', 'unknown')}': {e}", exc_info=True)
        return False

def handler(event, context):
    """
    Main Lambda handler function. Expects an HTTP GET with a 'sentence' query parameter.
    Parses the sentence, filters restaurants, and returns a recommendation.
    """
    logger.info(f"Incoming event: {json.dumps(event)}")

    # Extract sentence from query string
    sentence = None
    if event.get("queryStringParameters"):
        sentence = event["queryStringParameters"].get("sentence")

    if not sentence:
        logger.warning("Missing 'sentence' parameter in request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required query parameter: sentence"}),
            "headers": {"Content-Type": "application/json"}
        }

    # Parse filters from the sentence
    filters = parse_sentence(sentence)
    if not filters["style"]:
        logger.warning("No supported restaurant style was supplied")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"No supported restaurant style was supplied. Supported styles are [{KNOWN_STYLES}]"}),
            "headers": {"Content-Type": "application/json"}
        }

    try:
        # Query restaurants from DynamoDB using filters
        restaurants = get_filtered_restaurants(filters["style"], filters["vegetarian"], filters["deliveries"])

        # Filter further by checking if open now, if required
        for r in restaurants:
            if filters["open_now"] and not is_open(r):
                continue
            logger.info(f"Returning recommended restaurant: {r['name']}")
            return {
                "statusCode": 200,
                "body": json.dumps({"restaurantRecommendation": r}),
                "headers": {"Content-Type": "application/json"}
            }

        logger.info("No matching open restaurant found.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No matching restaurant found."}),
            "headers": {"Content-Type": "application/json"}
        }

    except RuntimeError as err:
        logger.error(f"Runtime error: {err}", exc_info=True)
        return {
            "statusCode": 503,
            "body": json.dumps({"error": "Service unavailable. Please try again later."}),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        logger.error("Unhandled exception occurred", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error."}),
            "headers": {"Content-Type": "application/json"}
        }
