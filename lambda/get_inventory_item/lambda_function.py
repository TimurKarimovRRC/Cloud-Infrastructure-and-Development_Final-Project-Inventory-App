import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types returned by DynamoDB."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):
    try:
        item_id = event.get("pathParameters", {}).get("id")

        if not item_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing item id"}),
            }

        # Query by partition key to find the item across any location
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("item_id").eq(item_id)
        )
        items = response.get("Items", [])

        if not items:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Item not found"}),
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(items[0], cls=DecimalEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
