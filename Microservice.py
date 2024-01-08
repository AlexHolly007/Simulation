# Written by  Alex Holly
# Description: This is the microservice file for the Simulation service. This only has one api function
#     which is used to choose an item at chance from an incomming http post request containing a dictionary.
#########
#########
from flask import Flask, request, render_template, jsonify
import random

app = Flask(__name__)



@app.route("/")
def main():
    return "hello world"



##
###
## This input to this function is a dictionary containing strings along with a probability for each string
## example input - {'apple': .3, 'orange': .5}
## This function will select one of the strings based on the probabilities given (it will always return one) by means
## of a JSON dictionary body reply.
@app.route('/random_num', methods=['POST'])
def modify_data():
    itemsAndProbabilities = request.get_json()
    print(f"BEEN HIT WITH REQUEST")
    print(f"cordinate keys{itemsAndProbabilities.keys()}") #check

    # Choose an item based on probability
    chosen_item = choose_item(itemsAndProbabilities)

    # Return the chosen item
    modified_data = {'result': chosen_item}
    return jsonify(modified_data)


def choose_item(probabilities):
    items = list(probabilities.keys())
    probabilities_list = list(probabilities.values())

    chosen_item = random.choices(items, probabilities_list)[0]
    return chosen_item

if __name__ == "__main__":
    app.run(debug=True, port=12121)
