from slackclient import SlackClient

import bot_conf
from bot_utils import log, log_warn, log_error


def bot_get_id(slackhandle):
    userscall = slackhandle.api_call("users.list")
    if userscall.get('ok'):
        users = userscall.get('members')
        botid = [user for user in users if 'name' in user and user.get('name') == bot_conf.BOT_NAME]
        botid = botid[0].get('id')
        log('Bot ID for tsimtakerbot is ' + str(botid))
    else:
        log_error("api error on get_id")


def bot_get_user_names(slackhandle):
    userscall = slackhandle.api_call("users.list")
    if userscall.get('ok'):
        users = userscall.get('members')
        usernames = [(user.get('id'), user.get('name')) for user in users if 'name' in user]
        return usernames
    log_warn("No users found?")
    return []


def bot_find_channel_id(slackhandle, channel_name):
    find_call = slackhandle.api_call("channels.list", exclude_archived=True, exclude_members=True)
    if find_call.get('ok'):
        channel_tokens = [chan for chan in find_call.get('channels')
                          if 'name' in chan and chan.get('name') == bot_conf.BOT_CHANNEL_NAME]
        if channel_tokens:
            channel_id = channel_tokens[0].get('id')
            return channel_id
        else:
            error_str = "Finding a channel failed: no channel with that name included in the list."
            log_error(error_str)
            raise RuntimeError(error_str)
    else:
        log_error("Finding a channel failed: " + str(find_call.get('error')))
        raise RuntimeError(str(find_call.get('error')))


if __name__ == """__main__""":
    slackhandle = SlackClient(bot_conf.BOT_API_TOKEN)
    bot_get_id(slackhandle)
