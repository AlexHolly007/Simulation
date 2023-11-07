from flask import Flask, request, render_template, jsonify
import os
import openai

#openai.organization = "org-66fOOihbBhRRMQ8kDRU9qoJY"
openai.api_key_path = 'templates/key.txt'

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/process-prompt', methods=['POST'])
def process_prompt():
    data = request.get_json()
    user_prompt = data['userPrompt']
    print (f"http prompt received: {user_prompt}")
    processed_prompt = f'You entered: {user_prompt}'
    
    return processed_prompt

@app.route('/generate_response', methods=['POST'])
def generate_response():
    user_input = request.form['user_input']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are creating a story with the user. You should make up an obsticle in the inputted situation and read it back as a continuation of the story, keep responses under 50 words"},
            {"role": "user", "content": f"{user_input}"} #animated, digital-art, warm
        ],
        max_tokens=50
    )
    return jsonify({'response': f'{response.choices[0].message.content}'})

if __name__ == '__main__': 
    app.run(debug=True, port=45454)
