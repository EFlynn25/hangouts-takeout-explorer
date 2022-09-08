# hangouts-takeout-explorer
Explore Hangouts chat data from Google Takeout

This is a python3 script that can let you traverse your chats right inside the command line. It could use some work but I've been able to get major nostalgia from my middle school days using it.

Usage:  
`python3 takeout_explorer.py <takeout_folder> [chat] [search]`

Args...  
`chat` -> search chat name OR chat index  
`search` -> search messages in chat (can be separated by spaces)

You can list all chats by not entering a chat or a search term. If there are multiple chats that contain your chat search term, it lists those chats with their indexes.
