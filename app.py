# Written by  Alex Holly
# Description: This is the main file for the Simulation service. This will connect
#     the javascript to the microservice, openai-gpt engines responses, and stable diffusion responses.
#     This file uses http post requests when requesting information from other API and returns JSON bodys that
#     include the needed responses
#########
#########

from flask import Flask, request, render_template, jsonify
import requests, json
from openai import OpenAI
from dotenv import load_dotenv

#loading api keys
##create a .env file containing OPENAI_API_KEY variable set to key
load_dotenv()
client = OpenAI()

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')




###
# Microservice function
# Sends the pre-made list of picture styles to the micro to randomly 
# select and return one based on the given probabilities
@app.route('/first_pic', methods=['POST'])
def first_pic():

    data = {'japanese anime':0.6, 'realistic':0.1, 'cartoon':0.1, 'comic':0.2}

    response = requests.post('http://localhost:12121/random_num', json=data)

    if response.status_code == 200:
        modified_data = response.json()
        #
        # Returns the data in a dictionary under key 'result'
        return modified_data, 200
    else:
        return jsonify({'message': 'Request failed', 'status_code': response.status_code}), response.status_code



#######
# Called to generate a response given the background of the story
# Sets the tone for the engine.
def get_story_response(player_input, story_state, chat_history, next_occurence):
    """
    player_input: str - The player's latest action or dialogue
    story_state: dict - Current story info (Location, Items, MainChar, NPCs, Goals)
    background: str - Static world/lore description
    chat_history: list - Previous turns, [{"role": "user"/"assistant", "content": "..."}]
    """

    #Building out the messege here
    system_messages = [
        {
            "role": "system",
            "content": (
                "You are a storytelling engine for a text-based, choose-your-own-adventure game. \
                Always write vivid immersive stories, but keep it simple so imagination can be up to \
                the user, and dont get too poetic. Keep events consistent and dont present too many at once \
                .Respond to the player's actions dynamically. Keep responses concise with less than 120 tokens."
            )
        },
        {
            "role": "system",
            "content": f"STORE STATE:\n{story_state}"
        },
    ]

    Output_intructions = [
        {
            "role": "system",
            "content": f"CONTINUATION INSTRUCTION: {next_occurence}"
        },
        {
            "role": "system",
            "content": (
                "OUTPUT INTRUCTIONS: 1. Story continuation using the CONTINUATION INSTRUCTION returned as normal text. 2. A  \
                JSON block summarizing the new story state that has same fields as STORY STATE passed before (Location, \
                Items, MainChar, NPCs, Goals). If those were empty, make them up using the user input \
                Format:\n"
                "---STORY---\n"
                "<narrative text>\n"
                "---STATE---\n"
                "{ \"Location\": ..., \"Items\": [...], \"MainChar\": ..., \"NPCs\": [...] \"Goals\": [...] }"
            )
        }
    ]

    #Compile package to send
    messages = system_messages + chat_history + [{"role": "user", "content": player_input}] + Output_intructions

    #SEND HER OFF
    response = client.chat.completions.create(
        model="gpt-5", 
        messages=messages,
        #max_completion_tokens= 400,
        #temperature=0.8,   unsupported for gpt 5
    )

    story_response = response.choices[0].message.content or ""

    # print("STORY RESPONSE:", story_response)
    # print("FULL RESPONSE:", response)

    #Get response and story state response
    if "---STATE---" in story_response:
        story, state_json = story_response.split("---STATE---", 1)
    else:
        #if model fails with this format
        story = story_response
        state_json = "{}"

    story = story.replace("---STORY---", "").strip()

    try:
        state_update = json.loads(state_json.strip())
    except json.JSONDecodeError:
        state_update = {}

    return story, state_update



###
# OpenAi response retrieval
# Sends: The user input, along with the history of chats within this story
# Returns: A generative text response based on the history of the OpenAI responses to create a cohesive story.
@app.route('/generate_response', methods=['POST'])
def generate_response():

    data = request.get_json()

    chat_history = data.get('chat_history')
    user_input = data.get('user_input')
    story_state = data.get('story_state')

    print("history:", chat_history)
    print("story state: ",story_state)
    print("input: ", user_input)

    ###
    ## The possible occurences to be sent to the microservice
    ## One will be selected and used for the response by the gpt response
    possible_occurences = {
        'a connection to a past part of the story': 0.2,
        'the story has an unexpected change': 0.2,
        'a spiney dragon with laser eyes appears': .01,
        'a new friend appears': 0.2,
        'a good occurance happens': 0.3,
        'a minor inconvenience/obsticle': 0.3,
        'a catastrophic obsticle has happened': 0.1,
        'The story ends': 0.05,
    }
    occurence_response = requests.post('http://localhost:12121/random_num', json=possible_occurences)
    json_occurence = occurence_response.json()
    occurence = json_occurence.get('result')
    print(f"occurance response: {occurence}")

    #
    # Creates the message to be sent to open-ai. Uses the chat history, the occurence, and the new user input.  
    story_response_text, story_state = get_story_response(user_input, story_state, chat_history, occurence)

    chat_history.append({'role': 'assistant', 'content': story_response_text})

    print('\nDONE WITH GPT API SENDING BACK TO JAVA FRONTEND\n')
    return jsonify({'response': story_response_text, 'chat_history': chat_history, 'story_state': story_state})




####
# Stability.ai API call to retrieve picture
# Sends the story situation for context, along with randomly choosen picture style
# Returns Json image that will be added into html within the javascript
@app.route('/get_picture', methods=['POST'])
def get_picture():

    data = request.get_json()
    image_text = data.get('image_text')
    style = data.get('style')
    print(f"style: {style}")
    url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"

    body = {
        "steps": 30,
        "width": 512,
        "height": 512,
        "seed": 0,
        "cfg_scale": 5,
        "samples": 1,
        "text_prompts": [
            {"text": f"{image_text}, bright, ","weight": 1},
            {"text": "blurry, splotchy, dark","weight": -1},
            {"text": f"{style} style of image","weight": 0.2}
        ],
    }

    with open('stable_key.txt', 'r') as file:
        stable_key = file.read().strip()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stable_key}",
    }
    response = requests.post(
        url,
        headers=headers,
        json=body,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    data = response.json()
    image_base64 = data["artifacts"][0]["base64"]

    print("\nDONE WITH PICTURE API, SENDING BACK TO SCRIPT\n")
    return jsonify({"image": image_base64})




if __name__ == '__main__': 
    app.run(debug=True, port=45454)
