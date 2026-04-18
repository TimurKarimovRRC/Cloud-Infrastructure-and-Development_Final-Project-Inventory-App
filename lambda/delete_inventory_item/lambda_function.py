import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def lambda_handler(event, context):
    try:
        item_id = event.get("pathParameters", {}).get("id")

        if not item_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing item id"}),
            }

        # Query to find the item first (need sort key for deletion)
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

        # Delete using both partition key and sort key
        table.delete_item(
            Key={
                "item_id": item_id,
                "item_location_id": items[0]["item_location_id"],
            }
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Item deleted successfully", "item_id": item_id}
            ),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
