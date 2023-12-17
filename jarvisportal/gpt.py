from openai import OpenAI
from time import sleep
import os
import json


class GPT:
    def __init__(self, assistant_id):
        self.client = OpenAI()
        # self.thread_id = self._get_or_create_thread_id() # expensive :(
        self.thread_id = self._create_thread_id()
        self.assistant_id = assistant_id
        self.last_messsage = None
        self.last_step_id = None
        self.run = None
        self._cancel_pending_runs()
    
    def _get_or_create_thread_id(self):
        threadfilename = "./.gptexecthread"
        if os.getenv("GPTEXEC_THREAD_ID"):
            thread_id = os.getenv("GPTEXEC_THREAD_ID")
            print(f"continuing GPT thread {thread_id}")
            return thread_id
        elif os.path.exists(threadfilename):
            with open(threadfilename, "r") as file:
                thread_id = file.read().strip()
            print(f"continuing GPT thread {thread_id}")
            return thread_id
        else:
            thread = self.client.beta.threads.create()
            with open(threadfilename, "w") as file:
                file.write(thread.id)
            print(f"created GPT thread {thread.id}")
            return thread.id

    def _create_thread_id(self):
            thread = self.client.beta.threads.create()
            print(f"created GPT thread {thread.id}")
            return thread.id
    
    def _cancel_pending_runs(self):
        pending_runs = [r for r in self.client.beta.threads.runs.list(thread_id=self.thread_id) if r.status in {"in_progress", "requires_action"}]
        for run in pending_runs:
            self.client.beta.threads.runs.cancel(thread_id=self.thread_id, run_id=run.id)
            print(f"canceled {run.status} run {run.id}")

    def send_chat(self, message):
        omessage = self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=message
        )
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id, assistant_id=self.assistant_id
        )
        self.last_messsage = omessage

    def next_answer(self):
        while self.run.status in ["queued", "in_progress"]:
            sleep(1)
            self.run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=self.run.id
            )
        answer = None
        if self.run.status == "completed":
            messages = list(
                self.client.beta.threads.messages.list(
                    thread_id=self.thread_id, before=self.last_messsage.id
                )
            )
            message = messages[0]
            answer = {
                "type": "message",
                "messages": [c.text.value for c in message.content],
                "is_final": True,
            }
            self.run = None
        elif self.run.status == "requires_action":
            steps = list(
                self.client.beta.threads.runs.steps.list(
                    thread_id=self.thread_id,
                    run_id=self.run.id,
                    order="asc",
                    after=self.last_step_id,
                )
            )
            step = steps[0]
            if step.step_details.type != 'message_creation': # still dont quite understand, but I know it doesn have too_calls
                try:
                    answer = {"type": "action", "actions": step.step_details.tool_calls}
                except:
                    print(step)
                    raise
            self.last_step_id = step.id
        elif self.run.status == "failed":
            message = "RUN FAILED."
            if self.run.last_error:
                message = f"{message} {self.run.last_error}"
            print(message)
        return answer

    def send_action_results(self, actions, results):
        self.run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run.id,
            tool_outputs=[
                {"tool_call_id": a["id"], "output": json.dumps(r)}
                for a, r in zip(actions, results)
            ],
        )

    # def is_done(self, run):
    #     return run.status in ["completed", "failed", "expired"]
