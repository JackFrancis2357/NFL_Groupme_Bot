# NFL Groupme Bot

## Overview
Groupme bot to track our NFL team bet. Myself and three friends each selected 8 NFL teams for the 2020 season. The player who has the fewest wins between their 8 teams has to buy drinks for the rest. Bot can be called in groupme with 'colts suck'. 

## Development and Deploying
App was built in Python and deployed on Heroku. I used the Heroku free tier and the Heroku CLI installer. Once you have Heroku CLI, login using 
'heroku login -i'

To hide the groupme_bot_id, I set it as a heroku environment variable. You can do this with:
'heroku config:set GROUPME_BOT_ID=[your bot id]'

Since the only objective was to keep track for our specific use case, most of the code is hard-coded. I recommend checking out Trent_Bot below for ideas on how to add further commands. I added Trent's code in the repo as an example of additional functionality that can be added to the bot. He has further explanation on these features in his repo linked below. AP_Norton's guide on creating a bot was also helpful. 

## Helpful Links
For further info on bot creating, see [Trent_Bot](https://github.com/trentprynn/TrentBot) and [AP_Norton_24_Hour_GroupMe_Bot](http://www.apnorton.com/blog/2017/02/28/How-I-wrote-a-Groupme-Chatbot-in-24-hours/)
