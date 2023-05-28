# ShikoniMessageString

Overview
``````
message_type: MessageType
message: String
``````
bytes
``````
# message type
shikoni:                        7 byte (string)
id_legth:                       1 byte (int)
type_id:                        id_legth bytes (int)

# ShikoniMessageString
lenght_message_legth:           1 byte (int)                            The lenght of the message legth
message_legth:                  lenght_message_legth bytes (int)
message:                        message_legth bytes (String)
``````
