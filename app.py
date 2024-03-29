from flask import Flask, render_template, request, jsonify, redirect
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

app = Flask(__name__)

thresholds = {
            'calories': 1500
        }

mqtt_broker_ip = "broker.emqx.io" 

sensorData = {}
burnedCalories = 0
lastStepCount = 0

# Create a callback function for handling incoming MQTT messages by accepting three parameters client, userData, msg
def on_message(client, userdata, msg):
    # Access sensorData as global
    global sensorData
    # Store topic from the msg in topic variable
    topic = msg.topic
    # Decode the message and store in payload
    payload = msg.payload.decode('utf-8')
    # Store the playload under the key topic in sensorData list
    sensorData[topic] = payload


# Create an MQTT client instance
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
# Set the callback function for incoming messages
mqtt_client.on_message = on_message
# Connect to the MQTT broker
mqtt_client.connect(mqtt_broker_ip, 1883, 60)
# Subscribe to the desired MQTT topics i.e "/Temperature", "/Humidity", "/Steps"
mqtt_client.subscribe("/Temperature")
mqtt_client.subscribe("/Humidity")
mqtt_client.subscribe("/Steps")
# Start the MQTT loop to listen for incoming messages
mqtt_client.loop_start()


@app.route('/')
def index():
    global thresholds
    return render_template('index2.html', thresholds=thresholds)

@app.route("/getSensorData", methods=['POST'])
def getSensorData():
    global burnedCalories, lastStepCount

    if(sensorData):
        newStepCount = int(float(sensorData['/Steps']))
        newSteps = int(newStepCount - lastStepCount)
        if(newSteps):
            newSteps = newStepCount - lastStepCount  
            temp = float(sensorData['/Temperature'] ) 
            hum = float(sensorData['/Humidity']  )
            
            calories = newSteps *(0.5 + temp/2000 + hum/2000)
            burnedCalories = burnedCalories + calories
            sensorData['burnedCalories'] = int(burnedCalories)
            
            lastStepCount = newStepCount
    return jsonify(sensorData)

@app.route('/setThresholds', methods=['POST'])
def set_thresholds():
    global thresholds
    if request.method == 'POST':
        calories = request.form.get('calories')

        thresholds = {
            'calories': calories
        }
        return redirect("/")
    
if __name__ == '__main__':
    app.run(debug=True)
