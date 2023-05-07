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
The messages are send in bytes to keep it open for all kind of messages to be send. 
To be able to know the message type, shikoni uses type_id with a combination of json to find the right Message class.

It should be possible to add new message types later on.

# Current status
I am still working on the base scripts. 
- ✅ Server Connection
- ✅ Clinet Connection
- ✅ start script
- ✅ search for free ports (API)
- ❌ forbit access for unauthorised users
- ❌ setup script
- ❌ make module and test it
- ❌ test run with tools
