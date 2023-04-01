import openai
import tiktoken

def setApiKey(key):
    openai.api_key = key



def talk(messages=None, text=None):
    print("talktring ")
    if messages is None:
        messages = [{"role": "user", "content": text}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    except Exception as e:
        print(e)
    print("res", response)
    messages.append(response.choices[0].message)
    return messages


def talkStream(messages=None, text=None):
    if messages is None:
        messages = [{"role": "user", "content": text}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )
    except Exception as e:
        print(e)
        return e
    return response


def messagesInitialize():
    with open("prompt_template.txt", "r") as f:
        s = f.read()
    return [{"role": "user", "content": s}]


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  
        tokens_per_name = -1 
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  
    return num_tokens
