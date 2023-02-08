# Powerful-Autofilter-Bot-Switch-


# Required Variables
BOT_TOKEN: The bot token
CHANNELS: Username or ID of channel or group. Separate multiple IDs by space
ADMINS: Username or ID of Admin. Separate multiple Admins by space
DATABASE_URI: mongoDB URI. Get this value from mongoDB. For more help watch this video
DATABASE_NAME: Name of the database in mongoDB. For more help watch this video

The easiest way to define those variables is creating a .env file in the root directory of the project and defining those variables in it. For example:

```
BOT_TOKEN = 1234567890:ABCDEFabcdef1234567890abcdefABCDEF
CHANNELS = FASDFADSF ASDFASDF ADFADSFADF
ADMINS = 123456789 987654321
DATABASE_URI = mongodb+srv://username:
DATABASE_NAME = autofilter
```

Create the bot and send /help to it. It will reply with the list of commands.



