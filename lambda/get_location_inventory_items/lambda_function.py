import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")

GSI_NAME = "item_location_id-item_id-index"


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
        location_id = event.get("pathParameters", {}).get("id")

        if not location_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing location id"}),
            }

        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=boto3.dynamodb.conditions.Key("item_location_id").eq(
                int(location_id)
            ),
        )
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(items, cls=DecimalEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
