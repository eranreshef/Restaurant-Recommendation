#!/usr/bin/env python3

import boto3
import json
import argparse

def normalize_item(item):
    return {
        "name": item["name"].lower(),
        "style": item["style"].lower(),
        "address": item["address"].lower(),
        "openHour": item["openHour"],
        "closeHour": item["closeHour"],
        "vegetarian": item["vegetarian"],
        "deliveries": item["deliveries"]
    }

def load_seed_data(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return [normalize_item(item) for item in data]

def seed_table(table_name, records):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    for item in records:
        print(f"Inserting: {item['name']}")
        table.put_item(Item=item)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to JSON file')
    parser.add_argument('--table', required=True, help='DynamoDB table name')
    args = parser.parse_args()

    items = load_seed_data(args.file)
    seed_table(args.table, items)

if __name__ == '__main__':
    main()
