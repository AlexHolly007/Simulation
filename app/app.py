# Written by  Alex Holly
# Description: This is the main file for the Simulation service. This will connect
#     the javascript to the microservice, openai-gpt engines responses, and stable diffusion responses.
#     This file uses http post requests when requesting information from other API and returns JSON bodys that
#     include the needed responses
#########
#TODO  Optional: Async the picture generation with the chat generation to be a little quicker
        #NOTE* since image is generated at same time at text, it no longer can use the most recent text
            #need to update the image generation prompts with that in mind

#TODO  check credits on openai, deploy to aws
#########

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
import requests, json, base64, tempfile, os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uvicorn
import httpx

#loading api keys
##create a .env file containing OPENAI_API_KEY variable set to key
load_dotenv() #fills env variables for keys
MICROSERVICE_URL = os.getenv("MICROSERVICE_URL", "http://localhost:12121") #grab docker microservice end if there
BASE_DIR = Path(__file__).resolve().parent

client = AsyncOpenAI()
# client = OpenAI()
app = FastAPI()



################.  DEV   ############################################
from starlette.staticfiles import StaticFiles
#noncaching for development to update no matter browser caching
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response
app.mount(f"/static", NoCacheStaticFiles(directory=f"{BASE_DIR}/static"), name="static")
####################################################################################



#front end just on this api port for now
#serve static index.html
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(f"{BASE_DIR}/templates/index.html") as f:
        return f.read()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#######
# Called to generate a response given the background of the story
# This is called by the generate response API endpoint below
# Sets the tone for the engine.
async def get_story_response(player_input, story_state, chat_history, next_occurence):
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
                "You are the engine for a text and image-based choose-your-own-adventure. "
                "The user writes prompts to advance the story, and you describe vivid, concise outcomes based on their input and any provided continuation "
                "The user is not part of the story unless explicitly stated. "
                "You may introduce environmental or character actions when needed, but the user dictates direction most of the time. "
                "Always match the user’s writing style, tone, and genre. Use common, natural language. Do not get too poetic. "
                "Keep responses under 120 tokens and describe only one clear event or change per turn. "
                "Avoid asking questions; show possibilities through action and detail instead. "
                "Maintain consistent pacing, tone, and formatting. "
                "If the user gives unclear or meta input (not story-related), request clarification instead of advancing the story."
            )
        }
    ]

    Output_intructions = [
        {
            "role": "system",
            "content": f"CONTINUATION INSTRUCTION: {next_occurence} \n \
                STORY STATE:\n{story_state}",
        },
        {
            "role": "system",
            "content": (
                "OUTPUT INTRUCTIONS: 1. normal narritive text return of story continuation using the CONTINUATION INSTRUCTION and user input.\n \
                2. A JSON block updating the new story state after the continuation. This has format of the STORY STATE passed before (but potentially \
                differnt values): Location, Characters. Can have empty values for things not yet established. \
                Format:\n"
                "---STORY---\n"
                "<narrative text>\n"
                "---STATE---\n"
                "{ \"Location\": ..., \"Characters\": [...] }"
            )
        }
    ]

    #Add player input to the history
    chat_history.append({"role": "user", "content": player_input})

    if len(chat_history) >= 6:
        chat_history = chat_history[-5:]

    #Compile package to send
    messages = system_messages + chat_history + Output_intructions

    #SEND HER OFF
    response = await client.chat.completions.create(
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



#LOOKS LIKE THIS BECAUSE WE ALWAYS EXPECT JSON OBJECT (DICTIONARY)
class GenerateRequest(BaseModel):
    user_input: str
    chat_history: list
    story_state: dict
###
# OpenAi response retrieval
# Sends: The user input, along with the history of chats within this story
# Returns: A generative text response based on the history of the OpenAI responses to create a cohesive story.
@app.post("/generate_response")
async def generate_response(data: GenerateRequest):
    user_input = data.user_input
    chat_history = data.chat_history
    story_state = data.story_state

    print("\nhistory:", chat_history)
    print("story state: ",story_state)
    print("input: ", user_input.strip())

    ###
    ## The possible occurences to be sent to the microservice
    ## One will be selected and used for the response by the gpt response
    possible_occurences = {
        'make a connection to a past part of the story': 0.1,
        'make the story have an unexpected change': 0.2,
        'have a spiney dragon with laser eyes appear': .01,
        'have a new friend appear': 0.2,
        'have the story continue as normal': 0.7,
        'make a good occurance happen': 0.2,
        'make a minor inconvenience/obsticle': 0.3,
        'make a catastrophic obsticle happen': 0.08,
        'make the story tragically end': 0.05,
    }
    #call microservice
    occurence_response = requests.post(f'{MICROSERVICE_URL}/random_num', json={"probs": possible_occurences})
    
    json_occurence = occurence_response.json()
    occurence = json_occurence.get('result')
    print(f"occurance response: {occurence}")

    #
    # Creates the message to be sent to open-ai. Uses the chat history, the occurence, and the new user input.  
    story_response_text, story_state = await get_story_response(user_input, story_state, chat_history, occurence)

    print("story state 2: ",story_state)

    chat_history.append({"role": "assistant", "content": story_response_text})

    print('DONE WITH GPT TEXT RESPONSE SENDING BACK TO JAVA FRONTEND\n')
    return {"response": story_response_text, "chat_history": chat_history, "story_state": story_state}




class PictureRequest(BaseModel):
    chat_history: list
    story_state: dict
    style: str
    last_image: str | None = None
####
# 
@app.post("/get_picture")
async def get_picture(data: PictureRequest):
    #chat history and story state for image context
    print("STARTING IMAGE BACKEND CALL FROM FASTAPI")
    chat_history = data.chat_history
    story_state = data.story_state
    style = data.style
    #last image to use same style, and character look
    last_image_base64 = data.last_image

    context_text = ''
    #there has been continuation
    if len(chat_history) > 2:
        story_summary = f"\n--NEW ACTION-->>> {chat_history[-1]['content']}"  # use only the last 2 messages to save tokens
        context_text = f"The story so far: LAST ACTION-->>{chat_history[-3]['content']}{story_summary}\nStory State: {story_state}\nArt style: {style}"
    
    #This is the first user prompt
    else:
        story_summary = "NEW ACTION-->>>", chat_history[-1]['content']
        context_text = f"The story so far: {story_summary}\nStory State: {story_state}\nArt style: {style}"


    last_image_path = None
    if last_image_base64:
        image_bytes = base64.b64decode(last_image_base64)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(image_bytes)
        temp_file.close()
        last_image_path = temp_file.name


    #input of the context and the last image
    gpt_image_prompt = f"You are a creative scene designer. This is an ongoing story, you need to generate the next image to give \
                the user a visual of whats going on in their story using the given context. Generate the image based on the NEW ACTION, \
                but If supplied an image and LAST ACTION, use the same style and make its continuation interpretable based off that image. \n \
                CONTEXT: {context_text}"

    img_response = None
    new_image_base64 = None
    #generate the image continue, or first image
    if last_image_path:
        # if you want to visually reference the previous image for consistency
        img_response = await client.images.edit(
            model="gpt-image-1",
            prompt=gpt_image_prompt,
            size="1024x1024",
            image=[open(last_image_path, "rb")]
        )

    else:
        #without a prior image
        img_response = await client.images.generate(
            model="gpt-image-1",
            prompt=gpt_image_prompt,
            n=1,
            size="1024x1024"
        )

    if img_response:
        new_image_base64 = img_response.data[0].b64_json # type: ignore

    #Clean up temporary image file
    if last_image_path:
        os.remove(last_image_path)

    print("BACKEND RETURNING IMAGE TO FRONT END")

    return ({"image": new_image_base64})



##Get picture style fastendpoint
# This endpoint is here because cant use env variables, and so it doesnt know 
# when the microservice endpoint changes.
# This is a redirect from the javascript to the microservice, and return as well
class picture_probs(BaseModel):
    probs: dict[str, float]
@app.post('/picture_style')
async def picture_style(data: picture_probs):

    #httpx yeilds this thread while waiting for a response
    response = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MICROSERVICE_URL}/random_num", json=data.model_dump()) #json={'probs': data.probs})
            return response.json()
    
    except Exception as e:
        print(f"ISSUE WITH CALLING MICROSERVICE FOR STYLE: {e} \n Response = {response}")
        return {"result": None}
    




if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=45454, reload=True)

#START WITH python3 app.py, autosetuo wuth vucirn
