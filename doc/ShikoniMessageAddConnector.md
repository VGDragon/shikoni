# ShikoniMessageAddConnector

Overview
``````
message_type: MessageType
message: ShikoniMessageAddConnector
    list:
        message_type: MessageType
        message: ShikoniMessageConnectorSocket
``````
bytes
``````
# message type
shikoni:                        7 byte (string)
id_legth:                       1 byte (int)
type_id:                        id_legth bytes (int)

# ShikoniMessageAddConnector
lenght_message_legth:           1 byte (int)                            The lenght of the message legth
message_legth:                  lenght_message_legth bytes (int)
legth_list_legth:               1 byte (int)                            The lenght of the list legth.
list_legth:                     legth_list_legth bytes (int)

# list of ShikoniMessageConnectorSocket
....
``````
