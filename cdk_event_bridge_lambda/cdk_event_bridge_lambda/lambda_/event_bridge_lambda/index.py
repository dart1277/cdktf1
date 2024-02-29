import json
import logging
import os
import tempfile

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


def handler(event, ctx):
    logger.info(event)
    logger.info(ctx)

    s3_bucket_name = os.environ["S3_BUCKET_NAME"]
    dynamodb_table_name = os.environ["DYNAMO_TABLE_NAME"]

    table = dynamodb.Table(name=dynamodb_table_name)

    response = table.scan()
    logger.info(response)

    for item in response['Items']:
        item_json = json.dumps(item)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write(item_json)
            tmp_file.close()

            s3_key = f'{dynamodb_table_name}/{item["id"]}.json'
            logger.info(f"Saving {s3_key}")
            s3_client.upload_file(tmp_file.name, s3_bucket_name, s3_key)

            os.remove(tmp_file.name)

            return {
                'statusCode': 200,
                'body': json.dumps({"message": "OK"})
            }


if __name__ == "__main__":
    s3_bucket_name = "test-bucket-123421234"
    dynamo_table_name = "test-table-123421234"
    os.environ["S3_BUCKET_NAME"] = s3_bucket_name
    os.environ["DYNAMO_TABLE_NAME"] = dynamo_table_name
    handler({}, {})
