import json
import sys
from datetime import datetime
from unittest.mock import patch

sys.path.append("..")
from api import lambda_handler


def test_parse_sentence():
    sentence = "Looking for vegetarian Indian food that offers delivery and is open now"
    result = lambda_handler.parse_sentence(sentence)
    assert result["style"] == "indian"
    assert result["vegetarian"] is True
    assert result["deliveries"] is True
    assert result["open_now"] is True


@patch("api.lambda_handler.table")
@patch("api.lambda_handler.logger")
def test_get_filtered_restaurants_with_filters(mock_logger, mock_table):
    mock_table.scan.return_value = {
        "Items": [{"name": "Pasta Place", "style": "italian", "vegetarian": True, "deliveries": True}]
    }

    result = lambda_handler.get_filtered_restaurants("italian", True, True)
    assert len(result) == 1
    assert result[0]["name"] == "Pasta Place"


@patch("api.lambda_handler.table")
def test_get_filtered_restaurants_no_filters(mock_table):
    mock_table.scan.return_value = {
        "Items": [{"name": "Any Place"}]
    }

    result = lambda_handler.get_filtered_restaurants()
    assert result[0]["name"] == "Any Place"


def test_is_open_true():
    restaurant = {"name": "Test", "openHour": "00:00", "closeHour": "23:59"}
    assert lambda_handler.is_open(restaurant) is True


@patch("api.lambda_handler.datetime")
def test_is_open_false(mock_datetime):
    mock_datetime.now.return_value = datetime.strptime("15:00", "%H:%M")
    mock_datetime.strptime = datetime.strptime

    restaurant = {"name": "Night Owl", "openHour": "22:00", "closeHour": "02:00"}
    assert lambda_handler.is_open(restaurant) is False


@patch("api.lambda_handler.get_filtered_restaurants")
@patch("api.lambda_handler.parse_sentence")
@patch("api.lambda_handler.logger")
def test_handler_success(mock_logger, mock_parse, mock_get_filtered):
    mock_parse.return_value = {
        "style": "mexican",
        "vegetarian": True,
        "deliveries": True,
        "open_now": False
    }
    mock_get_filtered.return_value = [
        {"name": "Taco Town", "openHour": "08:00", "closeHour": "20:00"}
    ]

    event = {
        "queryStringParameters": {
            "sentence": "Show me vegetarian Mexican places with delivery"
        }
    }

    result = lambda_handler.handler(event, None)
    body = json.loads(result["body"])
    assert result["statusCode"] == 200
    assert "restaurantRecommendation" in body


def test_handler_missing_sentence():
    event = {"queryStringParameters": {}}
    result = lambda_handler.handler(event, None)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body


@patch("api.lambda_handler.get_filtered_restaurants", side_effect=RuntimeError("DynamoDB is unavailable"))
@patch("api.lambda_handler.parse_sentence")
def test_handler_dynamodb_error(mock_parse, mock_get_filtered):
    mock_parse.return_value = {
        "style": "thai",
        "vegetarian": False,
        "deliveries": False,
        "open_now": False
    }

    event = {"queryStringParameters": {"sentence": "Thai food"}}
    result = lambda_handler.handler(event, None)
    assert result["statusCode"] == 503


@patch("api.lambda_handler.get_filtered_restaurants", side_effect=Exception("Unexpected"))
@patch("api.lambda_handler.parse_sentence")
def test_handler_unexpected_error(mock_parse, mock_get_filtered):
    mock_parse.return_value = {
        "style": "chinese",
        "vegetarian": False,
        "deliveries": False,
        "open_now": False
    }

    event = {"queryStringParameters": {"sentence": "Chinese food"}}
    result = lambda_handler.handler(event, None)
    assert result["statusCode"] == 500
