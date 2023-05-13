# Message

## base concept

Every message starts with the message type. The type is used to call the right class and encode the message.

To make that possible, we have a dictionary that contains the information of the existing message types.
If you want to extend that dictionary, you can make a JSON fine to extend or overwrite the used message classes.

Message
``````
message_type: MessageType
message
``````

Make sure that each variable has the following structure.

Example: String
``````
lenght_leght (int)
lenght (int)
string (string)
``````

If we want to send the string "Hello World!" with that structure, it would look like this.
To make is easier to see, I will use numbers as byte.
``````
1 # 1 byte
12 # 1 byte
Hello World! # 12 bytes
``````
With a longer text it would look like this

``````
2 # 1 byte
306 # 2 bytes
An byte can hold the number 0 to 255 
and if we want to count up more as 255, 
we need more as one bytes. 
Two bytes can go up to 65536 that could be enough,  
but with a long text even that could be to less for 
counting each character that is used. 
We want to save space and keep the possibility to grow.
# 306 bytes
``````

## A message in a message

The message itself can contain another message type.
With that approach, you have to handle each entry like it is a message itself.

Example: ShikoniMessageAddConnector
``````
message_type: MessageType
message: ShikoniMessageAddConnector
    list:
        message_type: MessageType
        message: ShikoniMessageConnectorSocket
``````
As bytes:
``````
# message type
shikoni:                        7 byte (string)
id_leght:                       1 byte (int)
type_id:                        id_leght bytes (int)

# ShikoniMessageAddConnector
lenght_message_leght:           1 byte (int)                            The lenght of the message leght
message_leght:                  lenght_message_leght bytes (int)
leght_list_leght:               1 byte (int)                            The lenght of the list leght.
list_leght:                     leght_list_leght bytes (int)

## list entry - repeat the following for list_leght times
## message type
shikoni:                        7 byte (string)
etry_id_legth:                  1 bytes (int)                           The lenght of the message_id legth.
etry_type_id:                   id_legth bytes (int)

## ShikoniMessageConnectorSocket
entry_legth_is_server:          1 byte (int)
entry_is_server:                entry_legth_is_server bytes (bool)
entry_legth_port:               1 byte (int)
entry_port:                     entry_legth_port bytes (int)
entry_legth_url:                1 byte (int)
etry_url:                       entry_legth_url bytes (int)
entry_legth_connection_name:    1 byte (int)
entry_connection_name:          entry_legth_connection_name bytes (int)

``````

## Custom message (interface)

We made an interface to have a baseline for encoding and decoding each message. It also includes a variable for
- message
- message_type
- shikoni

It also has functions to encode and decode the length bytes to not have to make your own one.

message:
- decode_io (BinaryIO for reading files)
- decode_bytes (bytearray)
- encode

help functions:
- decode_bytes_length (bytearray)
- decode_bytes_length_io (BinaryIO for reading files)
- encode_bytes_length (int)

It is preferred to use the super() function, because we may have to make changes to the interface later.

The [ShikoniMessageString](https://github.com/VGDragon/shikoni/blob/main/shikoni/message_types/ShikoniMessageString.py) file 
is a small class to get a felling how to work with the interface and the super() function.


