# ShikoniMessageConnectorName

Overview
``````
message_type: MessageType
is_server: Boolean
connection_name: String
``````
bytes
``````
# message type
shikoni:                                7 byte (string)
id_legth:                               1 byte (int)
type_id:                                id_legth bytes (int)

## ShikoniMessageConnectorName
legth_is_server_legth:                  1 byte (int)
is_server_legth:                        legth_is_server_legth byte (int)
is_server:                              is_server_legth bytes (bool)
legth_connection_name_length:           1 byte (int)
connection_name_length:                 legth_connection_name_length byte (int)
connection_name:                        legth_connection_name bytes (int)
``````
