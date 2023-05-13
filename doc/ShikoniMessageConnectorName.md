# ShikoniMessageAddConnector

Overview
``````
message_type: MessageType
message: ShikoniMessageConnectorName
``````
bytes
``````
# message type
shikoni:                        7 byte (string)
id_legth:                       1 byte (int)
type_id:                        id_legth bytes (int)

## ShikoniMessageConnectorName
entry_legth_is_server:          1 byte (int)
entry_is_server:                entry_legth_is_server bytes (bool)
entry_legth_connection_name:    1 byte (int)
entry_connection_name:          entry_legth_connection_name bytes (int)
``````
