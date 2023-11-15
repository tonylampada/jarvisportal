import sys
from openai import OpenAI
from openai.types.beta.threads.runs.run_step import RunStep
from time import sleep
import json
import subprocess
import shlex
import os

client = OpenAI()

ASSISTANT_ID = "asst_8AK25U8esouKTA56PLN7hqwa"
usr = '\U0001F600'
bot = '\U0001F916'
cmd = '\U0001F47B'


def action_runtest(path):
    print(f"{cmd} running test {path}...")
    exit_status, output = _cmdexec(f"npm run jest -- {path}")
    print(output)
    print(f"test status {exit_status}")
    return {"exit": exit_status, "output": output}


def action_getFile(path):
    print(f"{cmd} get file {path}")
    if not os.path.isfile(path):
        print("not found")
        return {"error": "file not found"}
    with open(path, "r") as file:
        result = file.read()
    return {"content": result}


def action_listDir(path):
    print(f"{cmd} list dir {path}")
    if not os.path.isdir(path):
        print("not found")
        return {"error": "directory not found"}
    contents = os.listdir(path)
    return {"contents": contents}


def action_updateFile(path, content):
    print(f"{cmd} update file {path}")
    with open(path, "w") as file:
        file.write(content)
    return {"success": True}

def action_exec(command):
    print(f"{cmd} exec {command}")
    exit_status, output = _cmdexec(command)
    print(output)
    print(f"command status {exit_status}")
    return {"exit": exit_status, "output": output}


def _cmdexec(cmd):
    process = subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ,
    )
    stdout, stderr = process.communicate()
    exit_status = process.wait()
    return exit_status, stdout.decode("utf-8") + stderr.decode("utf-8")


action_runners = {
    "runtest": action_runtest,
    "getFile": action_getFile,
    "listDir": action_listDir,
    "updateFile": action_updateFile,
    "exec": action_exec,
}


class GPT:
    def __init__(self):
        self.thread_id = client.beta.threads.create().id
        self.last_messsage = None
        self.last_response = None
        self.last_step_id = None

    def send_chat(self, message):
        omessage = client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=message
        )
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id, assistant_id=ASSISTANT_ID
        )
        self.last_messsage = omessage
        return run

    def next_response(self, run):
        while run.status in ["queued", "in_progress"]:
            sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=run.id
            )
            # print(run.status)
        response = None
        if run.status == "completed":
            messages = list(
                client.beta.threads.messages.list(
                    thread_id=self.thread_id, before=self.last_messsage.id
                )
            )
            message = messages[0]
            response = {
                "type": "message",
                "messages": [c.text.value for c in message.content],
            }
            self.last_response = message
        elif run.status == "requires_action":
            steps = list(
                client.beta.threads.runs.steps.list(
                    thread_id=self.thread_id,
                    run_id=run.id,
                    order="asc",
                    after=self.last_step_id,
                )
            )
            step = steps[0]
            if step.step_details.type != 'message_creation': # still dont quite understand, but I know it doesn have too_calls
                try:
                    response = {"type": "action", "actions": step.step_details.tool_calls}
                except:
                    print(step)
                    raise
            self.last_step_id = step.id
        elif run.status == "failed":
            message = "RUN FAILED."
            if run.last_error:
                message = f"{message} {run.last_error}"
            print(message)
        return response, run

    def send_action_results(self, run, results):
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=run.id,
            tool_outputs=[
                {"tool_call_id": r["id"], "output": json.dumps(r["output"])}
                for r in results
            ],
        )
        return run

    def is_done(self, run):
        return run.status in ["completed", "failed"]


def main(args):
    directory = args[0]
    gpt = GPT()
    while True:
        chatLoop(gpt)


def chatLoop(gpt):
    userInput = input(f"{usr} User: ")
    run = gpt.send_chat(userInput)
    while not gpt.is_done(run):
        print("waiting...")
        response, run = gpt.next_response(run)
        print("=========================================================")
        if response and response["type"] == "action":
            action_results = exec_actions(response["actions"])
            run = gpt.send_action_results(run, action_results)
        elif response and response["type"] == "message":
            print_messages(response["messages"])


def exec_actions(actions):
    return [_exec_action(action) for action in actions]

def _exec_action(action):
    try:
        return {
            "id": action["id"],
            "output": action_runners[action["function"]["name"]](
                **json.loads(action["function"]["arguments"])
            )
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "id": action["id"],
            "output": f"Error: {e}"
        }

def print_messages(messages):
    for message in messages:
        print(f"{bot} {message}")
        print(message)


if __name__ == "__main__":
    main(sys.argv[1:])


# ###
# gpt = GPT()
# run = gpt.send_chat("conserte o teste /testes/test1.js")
# response, run = gpt.next_response(run)
# results = exec_actions(response["actions"])
# run = gpt.send_action_results(run, results)
# response, run = gpt.next_response(run)
# print_messages(response["messages"])
