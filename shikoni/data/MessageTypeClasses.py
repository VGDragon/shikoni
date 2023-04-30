import json


def get_message_type_classes(message_type_decode_file: str = None):
    message_type_classes = get_default_message_type_classes()
    if message_type_decode_file is None:
        return message_type_classes

    with open(message_type_decode_file) as f:
        message_type_dictionary_from_file: dict = json.loads(f.read())

    for key, item in message_type_dictionary_from_file.items():
        message_type_classes[key] = item

    return message_type_classes

def get_default_message_type_classes():

    return {
        "1": {
            "module": "shikoni.base_messages.ShikoniMessageAddConnector",
            "class": "ShikoniMessageAddConnector"
        },
        "2": {
            "module": "shikoni.base_messages.ShikoniMessageConnectorSocket",
            "class": "ShikoniMessageConnectorSocket"
        },
        "3": {
            "module": "shikoni.base_messages.ShikoniMessageRemoveConnector",
            "class": "ShikoniMessageRemoveConnector"
        },
        "4": {
            "module": "shikoni.base_messages.ShikoniMessageConnectorName",
            "class": "ShikoniMessageConnectorName"
        },
        "101": {
            "module": "shikoni.message_types.ShikoniMessageString",
            "class": "ShikoniMessageString"
        },
        "102": {
            "module": "shikoni.message_types.ShikoniMessageInteger",
            "class": "ShikoniMessageInteger"
        }
    }
