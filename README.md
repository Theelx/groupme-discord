# GroupMeDiscord

This is a fork of karmanyaahm's amazing fork of the original Discord-Groupme bridge. Currently the only additions over karmanyaahm's version are the ability to relay images from Groupme chats to Discord (and vice versa), and the ability to host it using flask and apache, though I'm willing to add more if requested!

See HOSTING.md for information on how to host this with flask and apache on an Ubuntu VPS, the original README using ngrok remains below.

I highly recommend getting your own VPS and not using ngrok if possible, as a cheap VPS at somewhere like [Galaxygate](https://billing.galaxygate.net/aff.php?aff=107) (disclosure: affiliate link gives me 10% comission) can be $3/month with high performance as opposed to ngrok costing at least $5/month if you want any more than 40 connections/minute. A bridge between Discord and Groupme with only 1 person on each end can easily surpass 40 connections per minute (each message takes a connection to Discord and Groupme, so only 1 messages every 3 seconds) during active chatting.

---

Some Python scripts to interface between Discord and GroupMe.

## Requirements
These scripts require Python 3.6+. <br/>
Before starting, make sure that you install the requirements with:
```bash
cd ~/path/to/GroupMe/
python3 -m pip install -r requirements.txt
touch last_message_id.txt
touch groupme_channels.txt
```
If you have issues with the discord.py installation, use the following command:
```bash
python3 -m pip install -U https://github.com/Rapptz/discord.py/archive/rewrite.zip#egg=discord.py
```
You also need to be able to **expose the flask webserver.** <br/>
The easiest method to do this is by using the ngrok tool. View the documentation [here](https://ngrok.com/). <br/>
(Note that Theelx#4980 recommends using a VPS to host it, see HOSTING.md for instructions on that)
Once ngrok is setup and authorized, execute the following command to recieve your ngrok URL (you'll need this later):
```bash
ngrok http 5000
```
Keep this process running as you start the application.
### Discord Bot
In order to send messages from Discord to GroupMe, you will need to create a Bot Application. <br>
To do this, first go to https://discordapp.com/developers/applications/me and login with your Discord account. 
Click "New App", fill in your App name, then click "Create App".
![image](http://i.imgur.com/s7QbeCv.png) <br/>
You should be redirected to the application page of your bot. <br/> Scroll down to the following prompt and select "Create a Bot User": <br/>
![image](http://i.imgur.com/C8W4dw1.png) <br/>
You will now be able to view the token of your bot application.
![image](http://i.imgur.com/ODQDOFc.png) <br/>
Copy this token and paste it into your `credentials.py` file.

### Webhook
The webserver will be sending GroupMe messages to a dedicated channel by using a Discord Webhook. <br/>
To create a webhook, navigate to a channel's edit page and select "Webhooks". <br>
After creating a webhook, copy the webhook URL shown: <br/>
![image](http://i.imgur.com/rYzZ9gc.png) <br/>
And paste it into your config file:
![image](http://i.imgur.com/ZMHYt3y.png) <br>
There's just one more thing to do on the Discord side: enable User Settings -> Appearance -> Developer Mode and right click the channel that the webhook is using. Paste this number into your config file too.

## GroupMe
Now that you've set up the Discord constants, you'll also need to setup your GroupMe Bot. <br/>
Navigate to https://dev.groupme.com/bots, login with your GroupMe account, and click "Create Bot".
![image](http://i.imgur.com/uEAkype.png) <br/>
Fill in the appropriate fields, and in the **Callback URL** field, enter the URL that you got from ngrok.
![image](http://i.imgur.com/rrUasK3.png) <br/>
Once you've created the Bot, click on the bot's field to see the **Bot ID**. Copy this string and paste it in your config file: <br/>
![image](http://i.imgur.com/hRqS0JM.png)
![image](http://i.imgur.com/nooiph0.png) <br/>
One more to go! On the same page, click the "Access Token" button to retrieve your access token.
Copy this string and paste it into your config file: <br/>
![image](http://i.imgur.com/IpouBmi.png)
![image](http://i.imgur.com/sA8tZJU.png) <br/>


## Configuration
Replace all the values in app.py.sample and credentials.py.sample with their proper values (you'll need to use stuff from the previous setup sections), and then rename the files to remove the .sample ending. You should have app.py and credentials.py now, and then you're set to go to the next step!
## Usage
Create a folder named `images` inside this repo directory for image processing to work as intended.
Run the application:
```bash
python3 main.py
```
You should see any messages appear in the chosen Discord channel, and you will also be able to send messages and images to the GroupMe chat.
