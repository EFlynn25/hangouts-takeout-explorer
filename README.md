# hangouts-takeout-explorer
Explore Hangouts chat data from Google Takeout

This is a python3 script that allows you traverse your chats right inside the command line. It could use some work but I've been able to get major nostalgia from my middle school days using it.

Usage:  
`python3 takeout_explorer.py <takeout_folder> [chat] [search]`

Args...  
`chat` -> chat index OR search chat name  
`search` -> search messages in chat (can be separated by spaces)

To list all chats, leave chat arg and search arg blank. If there are multiple chats that contain your chat search term, it lists those chats with their indexes.

To view the entire chat, leave search arg blank.
