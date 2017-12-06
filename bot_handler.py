import time

import bot_conf
from bot_utils import log, log_error

LAST_STATUS_CHAT_MESSAGE = None


class TakenToken(object):
    def __init__(self):
        self.taken = False
        self.by_who = ""
        self.when = 0
        self.for_long = False


resources = { 'tsim': TakenToken(), 'grmon': TakenToken() }
status_icons = { True: ":res_taken:", False: ":res_free:" }


def bot_generate_status_message():
    def get_resource_status(resource_name):
        resource = resources[resource_name]
        status = resource_name.upper() + ": "
        status += status_icons[resource.taken]
        if resource.taken:
            status += " (" + resource.by_who
            if resource.for_long:
                status += ", for long"
            elif time.time() - resource.when >= bot_conf.BOT_AFK_DELAY:
                status += ", " + bot_conf.BOT_AFK_MESSAGE
            status += ")"
        return status

    status_message = ""
    status_message += get_resource_status('tsim')
    status_message += " / "
    status_message += get_resource_status('grmon')

    return status_message


def bot_take_resource(res, who, for_long):
    if not resources[res].taken:
        resources[res].taken = True
        resources[res].by_who = who
        resources[res].when = time.time()
        resources[res].for_long = for_long
        log("Resource " + res + " successfully taken by " + who + ("." if not for_long
                                                                   else ", for long."))
        return (True, bot_generate_status_message())

    response = "Resource take of " + res + " by " + who + " failed " \
        + "(already taken by " + resources[res].by_who + ")."
    log(response)
    return (False, response)


def bot_free_resource(res, who, for_long):
    if resources[res].taken and resources[res].by_who == who:
        time_held = time.time() - resources[res].when
        resources[res].taken = False
        resources[res].by_who = ""
        resources[res].when = 0
        resources[res].for_long = False
        log("Resource " + res + " successfully freed by " + who
            + ", held for " + str(int(time_held)) + " seconds.")
        return (True, bot_generate_status_message())

    response = "Resource free of " + res + " by " + who + " failed " \
        + ("(already freed)." if not resources[res].taken
           else "(held by " + resources[res].by_who + ").")

    log(response)
    return (False, response)


handling_commands = { bot_conf.BOT_TAKE_PREFIX: bot_take_resource,
                      bot_conf.BOT_FREE_PREFIX: bot_free_resource }


def bot_post_status_message(slackhandle, message):
    global LAST_STATUS_CHAT_MESSAGE

    msg_call = slackhandle.api_call("chat.postMessage", channel=bot_conf.BOT_CHANNEL_ID,
                                    text=message, as_user=True)
    if msg_call.get('ok') and 'ts' in msg_call:
        LAST_STATUS_CHAT_MESSAGE = msg_call.get('ts')
    else:
        log_error("Posting a status message failed with error: " + str(msg_call.get('error')))


def bot_delete_last_status_message(slackhandle):
    global LAST_STATUS_CHAT_MESSAGE
    if LAST_STATUS_CHAT_MESSAGE is not None:
        msg_call = slackhandle.api_call("chat.delete", channel=bot_conf.BOT_CHANNEL_ID,
                                        ts=LAST_STATUS_CHAT_MESSAGE, as_user=True)
        if msg_call.get('ok'):
            LAST_STATUS_CHAT_MESSAGE = None
        else:
            log_error("Deleting a status message failed with error: " + str(msg_call.get('error')))


def bot_handle_commands(slackhandle, command, channel, who):
    if command.startswith(bot_conf.BOT_TAKE_PREFIX) or command.startswith(bot_conf.BOT_FREE_PREFIX):
        try:
            for_long = False
            args = command.split(" ")
            resource_cmd = args[0][:5]
            resource = args[0][5:]
            if resource == "" and args[1] in resources:
                resource = args[1]
            if bot_conf.BOT_LONG_KEYWORD in args:
                for_long = True

            try:
                result = handling_commands[resource_cmd](resource, who, for_long)
                bot_delete_last_status_message(slackhandle)
                bot_post_status_message(slackhandle, result[1])
            except KeyError:
                bot_delete_last_status_message(slackhandle)
                bot_post_status_message(slackhandle, "Invalid resource: " + resource)
        except Exception as e:
            log_error("Exception caught while handling commands: " + str(e))
            raise
    elif command.startswith(bot_conf.BOT_STATUS_PREFIX):
        bot_delete_last_status_message(slackhandle)
        bot_post_status_message(slackhandle, bot_generate_status_message())
