from local_llm_function_calling import Generator
from local_llm_function_calling.model.llama import LlamaModel
from local_llm_function_calling.prompter

functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                    "maxLength": 20,
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    }
]

print("start")
generator = Generator(
    functions,
    LlamaModel(
        "codellama-13b-instruct.Q5_0.gguf"
    ),
)
print("generating...")

function_call = generator.generate("What is the weather like today in Brooklyn?")
print(function_call)
