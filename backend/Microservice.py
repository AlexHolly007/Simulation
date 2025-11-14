# Written by Alex Holly
# Description: This is the microservice file for the Simulation service. This only has one api function
#     Which is used to choose an item at chance from an incomming http post request containing a dictionary.
#########
#########

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Dict
import random
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins; replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],       # allow GET, POST, etc.
    allow_headers=["*"],       # allow all headers
)


#define data input
class Probabilities(BaseModel):
    probs: Dict[str, float]
##
###
## This input to this function is a dictionary containing strings along with a probability for each string
## example input - {'apple': .3, 'orange': .5}
## This function will select one of the strings based on the probabilities given (it will always return one) by means
@app.post("/random_num")
def modify_data(data: Probabilities):
    items_and_probs = data.probs

    print("HIT WITH RANDOM RESPONSE REQUEST")
    chosen_item = choose_item(items_and_probs)
    print(f"Chosen Item: {chosen_item}")
    print("RETURNING TO MAIN APP")

    return {"result": chosen_item}


def choose_item(probabilities):
    items = list(probabilities.keys())
    probabilities_list = list(probabilities.values())

    chosen_item = random.choices(items, probabilities_list)[0]
    return chosen_item

if __name__ == "__main__":
    #only called with command below. docker container doesnt call this
    uvicorn.run("Microservice:app", host="127.0.0.1", port=12121, reload=True)

#START UP WITH  python3 Microservice.py
