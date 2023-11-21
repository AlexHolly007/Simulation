
from flask import Flask, request, render_template, jsonify
import math as Math


app = Flask(__name__)

@app.route("/")
def main():
    return "hello world"

@app.route('/modify_data', methods=['POST'])
def modify_data():
    # Get data from the request
    data = request.get_json()

    lat1 = float(data['lat1'])
    lat2 = float(data['lat2'])
    lon1 = float(data['lon1'])
    lon2 = float(data['lon2'])

    # Using Haversines formula I calculate the distance between 2 points on the globe
    R = 3959 # Radius of the Earth in kilometers
    dLat = Math.radians(lat2 - lat1)
    dLon = Math.radians(lon2 - lon1)
    a = (
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(Math.radians(lat1)) * Math.cos(Math.radians(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
    )
    c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    distance = R * c

    modified_data = {'result': distance}

    # Return the modified data
    return jsonify(modified_data)

if __name__ == "__main__":
    app.run(debug=True, port=12121)

