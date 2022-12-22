import datetime
import json
from typing import Any

import boto3

DDB = boto3.client("dynamodb")


def update_extract_tracking_table(
    source: str,
    hwm_value: Any,
    lwm_value: Any,
    hwm_col_name: str,
    hwm_column_type: str,
    extract_type: str,
    extract_metadata: dict,
    extract_successful: str,
    tracking_table_name: str,
) -> None:
    """
    Inserts or updates an item in a DynamoDB table.

    If an item with the same partition key (source) already exists in the table,
    the item is updated with the new values. If no such item exists, a new item
    is inserted with the specified values.

    :params source (str): The partition key for the item.
    :params hwm_value (int): The value for the "hwm_value" field of the item.
    :params lwm_value (int): The value for the "lwm_value" field of the item.
    :params hwm_col_name (str): The value for the "hwm_col_name" field of the item.
    :params extract_type (str): The value for the "extract_type" field of the item.
    :params extract_metadata (dict): A dictionary containing the values for the "extract_metadata" field of the item.
    :params extract_successful (str): A Y or N to determine if the extract is successful.
    :params tracking_table_name (str): DDB Tracking Table name.
    """
    # Define the item to be inserted or updated
    item = {
        "source": {"S": source},
        "hwm_value": {"S": str(hwm_value)},
        "lwm_value": {"S": str(lwm_value)},
        "hwm_col_name": {"S": hwm_col_name},
        "hwm_column_type": {"S": hwm_column_type},
        "extract_type": {"S": extract_type},
        "updated_at": {"S": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
        "extract_successful": {"S": extract_successful},
        "extract_metadata": {"S": json.dumps(extract_metadata)},
    }

    # Use the `put_item` method to insert or update the item
    DDB.put_item(TableName=tracking_table_name, Item=item)


def get_tracking_table_item(source: str, tracking_table_name: str) -> dict:
    """
    Retrieves an item from a DynamoDB table based on its partition key.

    :params source (str): The partition key of the item to be retrieved.
    :params tracking_table_name (str): DDB Tracking Table name.
    :returns: The item, as a dictionary. If the item does not exist, returns False.
    """

    # Define the key of the item to be retrieved
    key = {"source": {"S": source}}

    # Use the `get_item` method to retrieve the item
    response = DDB.get_item(TableName=tracking_table_name, Key=key)

    # Return the item if it exists, or None if it doesn't
    return response.get("Item", False)
