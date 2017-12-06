from slackclient import SlackClient
import time

import bot_conf
from bot_id import bot_get_user_names, bot_find_channel_id
from bot_handler import bot_handle_commands
from bot_utils import log, log_error

slackhandle = SlackClient(bot_conf.BOT_API_TOKEN)
bot_id = bot_conf.BOT_USER_ID


def parse_slack_output(rtm_output):
    output_list = rtm_output
    if output_list is not None and output_list:
        for output in output_list:
            if output and 'text' in output:
                output_text = output.get('text').strip().lower()
                if output_text.startswith(bot_conf.BOT_TAKE_PREFIX) \
                        or output_text.startswith(bot_conf.BOT_FREE_PREFIX) \
                        or output_text.startswith(bot_conf.BOT_STATUS_PREFIX):
                    return output_text, output.get('channel'), output.get('user')
    return None, None, None


if __name__ == """__main__""":
    if slackhandle.rtm_connect():
        log("TsimTakerBot started.")

        bot_conf.BOT_CHANNEL_ID = bot_find_channel_id(slackhandle, bot_conf.BOT_CHANNEL_NAME)

        try:
            bot_handle_commands(slackhandle,
                                bot_conf.BOT_STATUS_PREFIX,
                                bot_conf.BOT_CHANNEL_ID,
                                None)
            while True:
                username = None
                command, channel, userid = parse_slack_output(slackhandle.rtm_read())
                if userid:
                    users_table = bot_get_user_names(slackhandle)
                    username = [user[1] for user in users_table if user[0] == userid][0]
                if command and channel and username:
                    log("Caught command: " + command + " from " + username)
                    bot_handle_commands(slackhandle, command, channel, username)
                time.sleep(bot_conf.BOT_READ_WEBSOCKET_DELAY)
        except KeyboardInterrupt:
            pass
    else:
        log_error("Connection failed.")
