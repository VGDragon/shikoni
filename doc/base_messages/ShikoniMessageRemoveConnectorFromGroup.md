# ShikoniMessageRemoveConnector

Overview
``````
message_type: MessageType
group_name: String
connector_name_list: list
    ShikoniMessageConnectorNamee
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
lenght_group_name_leght:        1 byte (int)                            The lenght of the group_name legth
group_name_leght:               lenght_group_name_leght bytes (int)
group_name:                     group_name_leght bytes (string)
legth_list_legth:               1 byte (int)                            The lenght of the list legth.
list_legth:                     legth_list_legth bytes (int)

# list of ShikoniMessageConnectorName
....
``````
