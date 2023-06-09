### Still Need testing
Some important parts will change until everything is ready for release.

# shikoni

This tool is for connection AI tools to combine them.

Github: [https://github.com/VGDragon/shikoni](https://github.com/VGDragon/shikoni)

## Idea
It could take a lot of computer power for tools and AI to run. It makes sense to seperate some tools or use a entrypoint.
The idea behind this project is to create an tool to make it easy to connect tools between computers.

Example:

You want to take an audio file (or microfon input) and want an AI to answer you with TTS.

Audio input, AI, TTS, Audio output


You make for each point an shikoni instance and conect them together if you need them. You take an shikoni instance and tell each point to connect to the next one.

```
Audio output: start server
TTS: start server, connect client to "Audio output"
AI: start server, connect client to "TTS"
Audio input: connect client to "AI"

Audio input -> AI -> TTS -> Audio output
```
If you want to switch the AI, you only need make an instance for that AI and keep the rest. You just have to remove the old connection and create the new one.

```
Audio input: disconnect client from "AI"
AI: stop server, disconnect client from "TTS"

AI_2: start server, connect client to "TTS"
Audio input: connect client to "AI_2"

Audio input -> AI_2 -> TTS -> Audio output
```

# Workflow
I try to make everything as easy to use as posible but stull have important functionality. 
The messages are send in bytes to keep it open for all kind of messages to be sent. 
To be able to know the message type, shikoni uses type_id with a combination of json to find the right Message class.

It should be possible to add new message types later on.

# Messages
In [doc](https://github.com/VGDragon/shikoni/blob/main/doc) you can find a description 
for each message that is currently implemented. 

For a base structure of each message, you can look at
[doc/message_overview.md](https://github.com/VGDragon/shikoni/blob/main/doc/message_overview.md)

I want to use the listed message structure to write shikoni in other programming languages, but first I want
to make it in python to be usable. The messages stricture should be the same for each language, to make a 
connection between all instances possible.

# Task before release
Some important parts can change until I am sure everything important is added.

I need some testing with different tools before I can make a real release.

# Current status
I am still working on the base scripts. 
- ✅ Server Connection
- ✅ Client Connection
- ✅ start script
- ✅ search for free ports (API)
- ✅ forbid access for unauthorised users (using path)
- ❌ setup script
- ❌ make module and test it
- ✅ test run with tools
