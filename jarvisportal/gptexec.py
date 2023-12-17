import sys
import os
from jarvisportal.gpt import GPT
from jarvisportal.llamaapichat import Chat as LlamaApiChat
from jarvisportal.actions import exec_actions, definitions

usr = '\U0001F600'
bot = '\U0001F916'
mic = '\U0001F3A4'

def main():
    args = sys.argv[1:]
    engine = os.getenv("CHAT_ENGINE", "gpt")
    if engine == "gpt":
        if len(args) != 1:
            print("Usage: gptexec.py <assistant_id>")
            exit(1)
        assistant_id = args[0]
        bot = GPT(assistant_id)
    elif engine == "llamaapi":
        bot = LlamaApiChat(definitions)
    try:
        while True:
            chatLoop(bot)
    except KeyboardInterrupt:
        print("\n====================================")
        print("Thank you for using GPTExec. Come back soon. ;)")
        print("====================================")

def _user_input():
    if os.getenv("GPTEXEC_VOICE") == "1":
        import jarvisportal.listentomic as listentomic
        userInput = listentomic.listen_and_transcribe(detectsilence=True)
        print(f"{usr} User: {userInput}")
    else:
        userInput = input(f"{usr} Type your message (or send an empty one to switch to voice input): \n")
        if userInput.strip() == "":
            print(f"{mic} Switching to voice input")
            import jarvisportal.listentomic as listentomic
            userInput = listentomic.listen_and_transcribe(detectsilence=False)
            print(f"{usr} User: {userInput}")
    return userInput    

def chatLoop(bot):
    userInput = _user_input()
    print("waiting...")
    bot.send_chat(userInput)
    answer = None
    while answer is None or not answer.get('is_final'):
        print("waiting...")
        answer = bot.next_answer()
        print("=========================================================")
        if answer["type"] == "action":
            action_results = exec_actions(answer["actions"], ask=True)
            bot.send_action_results(answer["actions"], action_results)
        elif answer["type"] == "message":
            print_messages(answer["messages"])

def print_messages(messages):
    for message in messages:
        print(f"{bot} {message}")


if __name__ == "__main__":
    main()
