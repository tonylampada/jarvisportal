from chatlab import Conversation
import openai
import asyncio
import os
import json
# openai.api_key = "functionary" # We just need to set this something other than None
os.environ['OPENAI_API_KEY'] = "functionary" # chatlab requires us to set this too
os.environ['OPENAI_BASE_URL'] = 'http://localhost:8000/v1'
# openai.api_base = "http://localhost:8000/v1"

# now provide the function with description
def get_car_price(car_name: str):
    """this function is used to get the price of the car given the name
    :param car_name: name of the car to get the price
    """
    car_price = {
        "tang": {"price": "$20000"},
        "song": {"price": "$25000"} 
    }
    for key in car_price:
        if key in car_name.lower():
            return {"price": car_price[key]}
    return {"price": "unknown"}

async def vai():
    print(os.environ.get("OPENAI_BASE_URL"))
    chat = Conversation(model="meetkai/functionary-7b-v1.1")
    # chat = Conversation()
    chat.register(get_car_price)  # register this function
    await chat.submit("what is the price of the car named Tang?") # submit user prompt
    # await chat.submit("Qual o preço do carro chamado Tang?") # submit user prompt
    print("[sent prompt]")

    # print the flow
    for message in chat.messages:
        # print(json.dumps(message))
        role = message["role"].upper()
        if "function_call" in message:
            func_name = message["function_call"]["name"]
            func_param = message["function_call"]["arguments"]
            print(f"{role}: call function: {func_name}, arguments:{func_param}")
        else:
            content = message["content"]
            print(f"{role}: {content}")

asyncio.run(vai())