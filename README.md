Simple script to import custom emoji from Slack and export to a Rocket.Chat instance.

Requires a Slack app to be configured against the target workspace. Also requires an admin user (with custom emoji permissions) on the Rocket.Chat instance. Due to the way the two APIs are set up, Slack requires a token and Rocket.Chat requires a username/password.

    python3 emoji_import.py --slack_token=<slack bot token> --rc_url=<rocketchat url> --rc_user=<rocketchat user> --rc_pass=<rocketchat pass>
