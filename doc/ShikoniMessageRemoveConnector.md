# ShikoniMessageAddConnector

Overview
``````
message_type: MessageType
message: ShikoniMessageRemoveConnector
    list:
        message_type: MessageType
        message: ShikoniMessageConnectorName
``````
bytes
``````
# message type
shikoni:                        7 byte (string)
id_legth:                       1 byte (int)
type_id:                        id_legth bytes (int)

# ShikoniMessageRemoveConnector
lenght_message_legth:           1 byte (int)                            The lenght of the message legth
message_legth:                  lenght_message_legth bytes (int)
legth_list_legth:               1 byte (int)                            The lenght of the list legth.
list_legth:                     legth_list_legth bytes (int)

# list of ShikoniMessageConnectorName
....
``````
