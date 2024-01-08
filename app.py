# Written by  Alex Holly
# Description: This is the main file for the Simulation service. This will connect
#     the javascript to the microservice, openai-gpt engines responses, and stable diffusion responses.
#     This file uses http post requests when requesting information from other API and returns JSON bodys that
#     include the needed responses
#########
#########

from flask import Flask, request, render_template, jsonify

import json, requests
import os
import openai
import base64

## Retrieves api key to make OpenAi calls.
openai.api_key_path = 'openai-key.txt'

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')




###
# Microservice function
# Sends the pre-made list of picture styles to the micro to randomly 
# select and return one based on the given probabilities
@app.route('/make_request', methods=['POST'])
def make_request():

    data = {'japanese anime':0.6, 'realistic':0.1, 'cartoon':0.1, 'comic':0.2}

    response = requests.post('http://localhost:12121/random_num', json=data)

    if response.status_code == 200:
        modified_data = response.json()
        #
        # Returns the data in a dictionary under key 'result'
        return modified_data, 200
    else:
        return jsonify({'message': 'Request failed', 'status_code': response.status_code}), response.status_code




###
# OpenAi response retrieval
# Sends: The user input, along with the history of chats within this story
# Returns: A generative text response based on the history of the OpenAI responses to create a cohesive story.
@app.route('/generate_response', methods=['POST'])
def generate_response():

    ###
    ## The possible occurences to be sent to the microservice
    ## One will be selected and used for the response by the gpt response
    possible_occurences = {
        'a connection to a past part of the story': 0.2,
        'nothing': 0.1,
        'a spiney dragon with laser eyes': .01,
        'a new freind': 0.2,
        'a good occurance': 0.3,
        'a minor inconvenience/obsticle': 0.2,
        'a return to a previous part of the story': 0.1,
    }
    occurence_response = requests.post('http://localhost:12121/random_num', json=possible_occurences)
    json_occurence = occurence_response.json()
    occurence = json_occurence.get('result')
    print(f"occurance response: {occurence}")

    data = request.get_json()
    backstory = data.get('backstory')
    user_input = data.get('user_input')
    print(backstory)
    print(user_input)

    #
    # Creates the message to be sent. Uses the backstory, the occurence, and the new user input.
    messages = backstory + [{"role": "system", "content": f"Include setting details like characters species and location, and add {occurence}"}] \
                            + [{"role": "user", "content": f"{user_input}"}]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100 #Maximum response of 100 characters.
    )

    backstory.append({'role': 'assistant', 'content': f'{response.choices[0].message.content}'})
    print('\nDONE WITH GPT API SENDING BACK TO JAVA\n')
    return jsonify({'response': f'{response.choices[0].message.content}', 'backstory': backstory})




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
