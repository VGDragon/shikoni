# ShikoniMessageConnectorSocket

Overview
``````
message_type: MessageType
is_server: Boolean
port: Integer
url: String
connection_name: String
connection_path: String
``````
bytes
``````
# message type
shikoni:                        7 byte (string)
id_legth:                       1 byte (int)
type_id:                        id_legth bytes (int)

## ShikoniMessageConnectorSocket
legth_is_server:                1 byte (int)
is_server:                      legth_is_server bytes (bool)
legth_port_length:              1 byte (int)
legth_port:                     legth_port_length byte (int)
port:                           legth_port bytes (int)
legth_url_legth:                1 byte (int)
legth_url:                      legth_url_legth bytes (int)
url:                            legth_url bytes (string)
legth_connection_name_legth:    1 byte (int)
legth_connection_name:          legth_connection_name_legth bytes (int)
connection_name:                legth_connection_name bytes (string)
legth_connection_path_legth:    1 byte (int)
legth_connection_path:          legth_connection_path byte (int)
connection_path:                legth_connection_path bytes (string)
``````
