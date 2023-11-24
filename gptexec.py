import sys
import os
from gpt import GPT
from actions import exec_actions

usr = '\U0001F600'
bot = '\U0001F916'
mic = '\U0001F3A4'

def main(args):
    assistant_id = args[0]
    gpt = GPT(assistant_id)
    gpt.cancel_pending_runs()
    try:
        while True:
            chatLoop(gpt)
    except KeyboardInterrupt:
        print("Exiting...")

def chatLoop(gpt):
    if os.getenv("GPTEXEC_VOICE") == "1":
        import listentomic
        userInput = listentomic.listen_and_transcribe()
        print(f"{usr} User: {userInput}")
    else:
        userInput = input(f"{usr} Type your message (or send an empty one to switch to voice input): \n")
        if userInput.strip() == "":
            print(f"{mic} Switching to voice input")
            import listentomic
            userInput = listentomic.listen_and_transcribe()
            print(f"{usr} User: {userInput}")
    run = gpt.send_chat(userInput)
    while not gpt.is_done(run):
        print("waiting...")
        response, run = gpt.next_response(run)
        print("=========================================================")
        if response and response["type"] == "action":
            action_results = exec_actions(response["actions"], ask=True)
            run = gpt.send_action_results(run, action_results)
        elif response and response["type"] == "message":
            print_messages(response["messages"])

def print_messages(messages):
    for message in messages:
        print(f"{bot} {message}")


if __name__ == "__main__":
    main(sys.argv[1:])
