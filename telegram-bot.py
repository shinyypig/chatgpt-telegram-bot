# import libraries
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import openai
import os

# get environment variables
# OpenAI key
openai_key = os.getenv('OPENAI_KEY')
print('OpenAI key: ', openai_key)

# Telegram bot key
bot_token = os.getenv('TELEGRAM_KEY')
print('Telegram bot key: ', bot_token)

# Telegram user id
user_id = os.getenv('TELEGRAM_USER_ID')
user_id = [int(i) for i in user_id.replace(
    '[', '').replace(']', '').split(',')]
print('Telegram user id: ', user_id)

# session limit
session_limit = int(os.getenv('SESSION_LIMIT'))
print('session limit: ', session_limit)


class ChatBot:
    # ChatBot class
    # the default prompt
    prompt = [{
        'role': 'system',
        'content': '我是一个 Telegram 机器人，我将以 markdown 语法修饰我的回答。'
    }]

    msg = []

    # init the class, set the OpenAI key and the limit of the prompt
    # the limit is the number of the last sessions to be used as the prompt
    def __init__(self, openai_key, limit=5):
        openai.api_key = openai_key
        self.limit = limit

    # get the response from OpenAI
    def get_response(self):
        if len(self.msg) == 0:
            messages = self.prompt
        else:
            messages = self.prompt + self.msg

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return completion.choices[0].message

    # convert the msg to a string
    def dict2string(self):
        if len(self.msg) == 0:
            messages = self.prompt
        else:
            messages = self.prompt + self.msg

        string = ''
        for msg in messages:
            print(msg)
            string += msg['role'] + ': ' + msg['content'] + '\n'
        return string

    # limit the number of the last sessions to be used
    def limit_msg(self):
        self.msg = self.msg[-self.limit*2:]

    # print the histroy of the conversation
    def print_all(self):
        print(self.dict2string())

    # ask OpenAI and update the histroy
    def askOpenai(self, question):
        self.msg.append({'role': 'user', 'content': question})
        self.print_all()
        response = self.get_response()
        self.msg.append(response)
        self.limit_msg()
        return response['content']


# define the handlers
# print the histroy by send /print to the telegram bot
async def print_histroy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id in user_id:
        string = chatbot.dict2string()
        await update.message.reply_text(string)


# clear the histroy by send /clear to the telegram bot
async def clear_histroy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id in user_id:
        chatbot.msg = []
        await update.message.reply_text("Histroy is cleared.")


# set the prompt by send /set to the telegram bot
async def set_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id in user_id:
        old_prompt = chatbot.prompt[0]['content']
        prompt = update.message.text[5:]
        chatbot.prompt[0]['content'] = prompt
        await context.bot.send_message(chat_id=update.effective_chat.id, text=old_prompt + '\nis changed to\n' + prompt)


# ask OpenAI and send the response to the telegram bot
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in user_id:
        try:
            response = chatbot.askOpenai(update.message.text)
        except Exception as e:
            response = 'GPT3 no response.'
            print(e)
        chatbot.print_all()
        if response:
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='MarkdownV2')
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=response+'\n\n Can not parse this response.\n')
                print(e)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='ChatGPT can not answer this question.')

chatbot = ChatBot(openai_key, session_limit*2)
chatbot.print_all()


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("print", print_histroy))
    application.add_handler(CommandHandler("clear", clear_histroy))
    application.add_handler(CommandHandler("set", set_prompt))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
