# GPT3.5 Telegram Bot

OpenAI chatbot for Telegram using GPT-3.5. Generally, the bot will respond to any message you send to it and render the text in a nice format. You can also use the `/print` command to print the chat history, and the `/clear` command to clear the chat history.

Command reference:

``` text
/print - Print the talk sessions.
/clear - Clear the talk sessions.
/set - Set the prompt.
```

## Docker Deployment

``` yaml
version: "3"
services:
  chatgpt-tgbot:
    image: shinyypig/chatgpt-tgbot:latest
    container_name: chatgpt-bot
    environment:
        - OPENAI_KEY=Your OpenAI API Key
        - TELEGRAM_KEY=Your Telegram Bot Token
        - TELEGRAM_USER_ID=[Your Telegram User ID].
        - SESSION_LIMIT=5 # The number of sessions to send to OpenAI.
        - PYTHONUNBUFFERED=1 # See python print in docker logs.
    restart: unless-stopped
```

Note that this bot only response to the user specified in `TELEGRAM_USER_ID`, and the `TELEGRAM_USER_ID` is a list so that multiple users can use this bot, e.g., `TELEGRAM_USER_ID=[213980, 214031]`.

## Prompt

The prompt send to OpenAI has the following format:

```text
{
    'role': 'system',
    'content': 'I am a Telegram robot, I will reply your question in markdown format.'
}
```

You can change the prompt by using the `/set` command. For example, if you are Chinese, you can change the prompt to Chinese:

``` text
/set 我是一个 Telegram 机器人，我将以 markdown 语法修饰我的回答。
```

Meawhile, this code only save the last `SESSION_LIMIT` sessions. You can use the `/print` command to print the histro, and the `/clear` command to clear the history.
