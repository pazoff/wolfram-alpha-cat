from cat.mad_hatter.decorators import tool, hook, plugin
from cat.log import log
from pydantic import BaseModel
import wolframalpha


# Settings

class WolframAlphaCatSettings(BaseModel):
    wolfram_alpha_App_ID: str

# Give your settings schema to the Cat.
@plugin
def settings_schema():
    return WolframAlphaCatSettings.schema()

def query_wolfram_alpha(query, cat):
    # Load the plugin settings
    settings = cat.mad_hatter.get_plugin().load_settings()
    wolfram_alpha_App_ID = settings.get("wolfram_alpha_App_ID")

    # Check for a wolfram_alpha_App_ID
    if (wolfram_alpha_App_ID is None) or (wolfram_alpha_App_ID == ""):
        no_app_id = 'Missing Wolfram Alpha App ID in the plugin settings. Get the App ID from: https://products.wolframalpha.com/api'
        return no_app_id

    try:
        # Initialize the Wolfram Alpha client
        client = wolframalpha.Client(wolfram_alpha_App_ID)

        result_text = ""  # Initialize an empty string to accumulate results

        res = client.query(query)

        for pod in res.pods:
            for sub in pod.subpods:
                if sub.plaintext is not None:
                    result_text += sub.plaintext + " <br><br> "  # Append plaintext result to the string variable

        if len(result_text) == 0:
            return "Wolfram Alpha returned no results."
        else:
            #cat.send_ws_message(content=' The Cat is Thinking ...', msg_type='chat_token')
            #llm_result = cat.llm(f"{query} based on: {result_text}")
            return result_text

    except Exception as e:
        # Handle any exceptions that occur during the Wolfram Alpha query
        error_message = f"Wolfram Alpha Cat: An error occurred: {str(e)}"
        return error_message


@hook(priority=5)
def agent_fast_reply(fast_reply, cat):
    return_direct = True

    # Get user message from the working memory
    message = cat.working_memory["user_message_json"]["text"]
    
    # Check if the message ends with '~'
    if message.endswith('~'):
        # Remove '~' 
        message = message[:-1]
        
        cat.send_ws_message(content='Querying Wolfram Alpha for ' + message + ' ...', msg_type='chat_token')
        result_from_wolframalpha = query_wolfram_alpha(message, cat)

        #log.warning(result_from_wolframalpha)
        print(result_from_wolframalpha)
        return {"output": result_from_wolframalpha}

    return None
