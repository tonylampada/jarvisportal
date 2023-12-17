import json
import os

from llamaapi import LlamaAPI

llama = LlamaAPI(os.getenv("LLAMA_API_KEY"))

# model = "llama-13b-chat"
model = "codellama-34b-instruct"

systemprompt = """
# Purpose
Your job is to help me as a developer.

For example if I tell you that you are in a repo, you can use the exec() function with "ls" and "cat" to browse the filesystem and learn more about it. Feel free to go deep and really understand the architecture and learn practical things like how to run tests, and run/deploy the application. If you find a "README.llm" file in there, definitely read it. Those are instructions specifically made for you to learn more about that repo.

If I ask for help fixing a test, and you know how to run it, you can run the test, read the code in the filesystem to understand why it breaks, use the functions createFile() and updateFile() to modify the filesystem and try again. To keep my API costs low, make at most 3 attempts until the test passes, then we can talk some more.

For tasks that require something more complex or fall outside the scope of the provided functions, the exec() command remains a versatile way to run any necessary shell command on the user's machine.

# Running functions

Important: 
- When using the functions, remember to properly escape backslashes, newlines, and double quotes in file contents when using the updateFile function. Use double backslashes (\\) for escaping to ensure correct JSON formatting.

# Language style and tone
Unless the user specifically asks you to explain something to them, you will give really succint answers with at most two sentences. 
For example, if the user tells you to scan a folder or a file, you should not give a lengthy explanation about what you just saw. Just a two line summary is more than enough. But if they ask you "how"/"why"... then you can be a little more verbose. A LITTLE. :-)

Also, let's make it fun. You have a light personality, not very serious, playful.
"""

class Chat:
    def __init__(self, functions):
        self.messages = [
            {"role": "system", "content": systemprompt},
        ]
        self.functions = functions

    def send_chat(self, msg):
        self.messages.append({"role": "user", "content": msg})
        self.last_response = self._send()
    
    def next_answer(self):
        if self.last_response.get("function_call"):
            answer = {
                "type": "action",
                "is_final": False,
                "actions": [{"function": self.last_response["function_call"]}]
            }
        else:
            answer = {
                "type": "message",
                "is_final": True,
                "messages": [self.last_response["content"]]
            }
        return answer

    def send_action_results(self, actions, results):
        self.messages.append({"role": "user", "content": json.dumps(results[0])})
        self.last_response = self._send()

    def _send(self):
        api_request_json = {
            "model": model,
            "functions": self.functions,
            "stream": False,
            "messages": self.messages,
        }
        response = llama.run(api_request_json)
        result = response.json()["choices"][0]["message"]
        if result.get("function_call"):
            fncall = result["function_call"]
            self.messages.append(
                {"role": "assistant", "content": json.dumps(fncall)}
            )
        else:
            self.messages.append({"role": "assistant", "content": result["content"]})
        # if self.executor and result.get("function_call"):
        #     fncall = result["function_call"]
        #     fnresult = self.executor.execute(fncall)
        #     result = self.sendFnresult(fncall["name"], fnresult)
        # else:
        #     self.messages.append({"role": "assistant", "content": result["content"]})
        return result
