import boto3
import json
import logging
import time
from pathlib import Path

log_level = logging.INFO
logging.basicConfig(level=log_level)
log = logging.getLogger(__name__)


def upload_data(table, emails):
    for key in emails:
        item = dict()
        item["filename"] = key
        item["Received_date"] = emails[key].pop("Received_date")
        item["data"] = emails[key]
        table.put_item(Item=item)
    log.info("Upload complete")


def get_table(dynamo_conn, table_name):
    try:
        log.info("Trying to create table %s", table_name)
        # Create the DynamoDB table.
        table = dynamo_conn.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "filename", "KeyType": "HASH"},  # partition key
                {"AttributeName": "Received_date", "KeyType": "RANGE"},  # sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "filename", "AttributeType": "S"},  # string
                {"AttributeName": "Received_date", "AttributeType": "S"},  # string
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,  # ReadCapacityUnits set to 5 strongly consistent reads per second
                "WriteCapacityUnits": 5,  # WriteCapacityUnits set to 5 writes per second
            },
        )
        # Wait until the table exists.
        table.wait_until_exists()
        log.info("table created")
        return table
    except:  # find the specific exception
        log.info("table %s already exists, returning it", table_name)
        return dynamo_conn.Table(table_name)


def main():
    start_time = time.monotonic()
    # json_folder = "/home/rjanssen/Mail/"
    json_folder = "/mnt/c/wsl_shared/enron/enron1"
    json_file = "cleaned_spam_emails.json"
    # json_file = "cleaned_emails_script.json"
    # json_file = "cleaned_emails_ascii.json"

    log.info("Reading json")
    with open(Path(json_folder, json_file)) as file:
        mails_dict = json.load(file)
    log.info("Read in %d items", len(mails_dict))

    log.info("Trying to connect to DynamoDB")
    try:
        # this is a resource, we could also use the client with "boto3.client"
        dynamodb = boto3.resource(
            "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-central-1"
        )
        log.info("Connection established")
    except:  # this does not seem to work
        log.critical("Connection to DynamoDB could not be established")
    our_table = "spam1"  # Emails and spam1
    table = get_table(dynamodb, our_table)
    log.info("Status: %s", table.table_status)
    old_count = table.item_count
    log.info("Items in table %d", old_count)
    log.info("Starting to upload data")
    upload_data(table, mails_dict)
    new_count = table.item_count
    log.info("Now %d items in table", new_count)
    # assert (new_count-old_count) == len(mails_dict)
    end_time = time.monotonic()
    log.info(
        "Uploading to DynamoDB done, elapsed time %ss", round(end_time - start_time, 1)
    )


if __name__ == "__main__":
    main()
