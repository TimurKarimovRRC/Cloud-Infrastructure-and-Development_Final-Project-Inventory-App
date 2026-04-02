import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        # Validate required fields
        required = ["item_id", "item_name", "item_description",
                     "item_qty_on_hand", "item_price", "item_location_id"]
        missing = [f for f in required if f not in body]

        if missing:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Missing required fields: {', '.join(missing)}"
                }),
            }

        item = {
            "item_id": body["item_id"],
            "item_name": body["item_name"],
            "item_description": body["item_description"],
            "item_qty_on_hand": int(body["item_qty_on_hand"]),
            "item_price": Decimal(str(body["item_price"])),
            "item_location_id": int(body["item_location_id"]),
        }

        table.put_item(Item=item)

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Item added successfully",
                                "item_id": item["item_id"]}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }