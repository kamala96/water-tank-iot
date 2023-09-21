from django.conf import settings
import paho.mqtt.client as mqtt
import threading
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from devices.models import MQTTStatus, Processor, WaterPump, WaterTankSensor

# from .consumers import WebSocketConsumer


class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        self.channel_layer = get_channel_layer()

        self.connected = False
        self.subscribed_topics = {}
        self.received_messages = {}

        # Create a thread to run the MQTT client loop
        self.mqtt_thread = threading.Thread(target=self.start_mqtt_client)
        self.mqtt_thread.daemon = True
        self.mqtt_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(
                f"Connected to MQTT Broker [{settings.MQTT_SERVER}:{settings.MQTT_PORT}]")
            self.connected = True

            # Update the MQTT connection status in the database
            mqtt_status, created = MQTTStatus.objects.get_or_create(pk=1)
            mqtt_status.set_connected(True)

            # Subscribe to the previously registered topics
            for topic, qos in self.subscribed_topics.items():
                client.subscribe(topic, qos)
        else:
            print(
                f"Failed to connect to MQTT Broker [{settings.MQTT_SERVER}:{settings.MQTT_PORT}]")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Disconnected from MQTT Broker. Reconnecting...")
            self.connected = False

            # Update the MQTT connection status in the database
            mqtt_status, created = MQTTStatus.objects.get_or_create(pk=1)
            mqtt_status.set_connected(False)

            self.client.reconnect()
            # self.start_mqtt_client()

    def on_message(self, client, userdata, msg):
        print('###########################')
        print(f'MQTT Received Message')
        print('---------------------------')
        print(f'Topic: {msg.topic}, Message: {msg.payload.decode("utf-8")}')
        print('###########################')
        # Store the received message in the dictionary
        self.received_messages[msg.topic] = msg.payload.decode('utf-8')

        # Extract the Institution/Owner/User part from the MQTT topic
        global institution  # Declare institution as a global variable
        message_topic = msg.topic
        topic_parts = message_topic.split('/')

        if len(topic_parts) >= 1:
            institution = topic_parts[0]

        if institution is not None:
            try:
                mqtt_action = topic_parts[-1]
                processor_mqtt_topic = topic_parts[1]

                # Get Micro-processor object
                processor_obj = Processor.objects.filter(
                    owner__mqtt_topic=institution, mqtt_topic=processor_mqtt_topic).first()

                mqtt_data = None
                if mqtt_action == 'CurrentLevel':
                    tank_mqtt_topic = topic_parts[-2]
                    # Get tank object
                    tank_obj = WaterTankSensor.objects.filter(
                        mqtt_topic=tank_mqtt_topic, processor=processor_obj).first()
                    if tank_obj is not None:
                        # Update water level
                        sent_water_level = float(msg.payload.decode('utf-8'))
                        tank_obj.set_current_level(new_level=sent_water_level)
                        updatedTankData = {
                            'id': tank_obj.mqtt_topic,
                            'name': tank_obj.name,
                            'percentage': tank_obj.calculate_percentage(),
                        }

                        # Create a dictionary containing both topic and message update
                        mqtt_data = {
                            "topic": message_topic,
                            "data": updatedTankData
                        }

                elif mqtt_action in ['PumpStatus', 'PumpStatusManual']:
                    pump_mqtt_topic = topic_parts[-2]

                    # Get pump object
                    pump_obj = WaterPump.objects.filter(
                        mqtt_topic=pump_mqtt_topic, switch__processor=processor_obj).first()
                    if pump_obj is not None:
                        # Update pump status
                        _message = str(msg.payload.decode('utf-8'))
                        if _message in ['On', 'Off']:
                            status = True if _message == 'On' else False
                            pump_obj.set_status(new_status=status)

                            if mqtt_action == 'PumpStatusManual':
                                topic_parts[-1] = 'PumpStatus'
                                message_topic = "/".join(topic_parts)
                            mqtt_data = {
                                "topic": message_topic,
                                "data": _message
                            }

                else:
                    pass

                if mqtt_data is not None:
                    # Trigger a websocket consumer method on channel when a new MQTT message is received
                    async_to_sync(self.channel_layer.group_send)(
                        f'account_{str(institution)}', {"type": "account.message", "message": mqtt_data})
            except Exception as e:
                # Handle any other exceptions that may occur
                print("An error occurred:", str(e))

    def start_mqtt_client(self):
        while True:
            try:
                self.client.connect(
                    host=settings.MQTT_SERVER,
                    port=settings.MQTT_PORT,
                    keepalive=settings.MQTT_KEEPALIVE
                )
                self.client.loop_forever()
            except (ConnectionRefusedError, OSError, Exception) as e:
                print(
                    f"Connection to MQTT Broker [{settings.MQTT_SERVER}:{settings.MQTT_PORT}] failed: {str(e)}. Retrying in 10 seconds...")
                self.connected = False
                time.sleep(10)  # Retry after 10 seconds

    def subscribe_topic(self, topic, qos=0):
        if self.connected:
            self.client.subscribe(topic, qos)
            print('--------------------------------')
            print(f'Subscribed to MQTT topic: {topic}')
            print('--------------------------------')
        else:
            # If not connected, store the topic for later subscription
            # print(f'MQTT service not ready, topics are in reserve list')
            self.subscribed_topics[topic] = qos

    def publish_to_mqtt_topic(self, topic, message):
        if self.connected:
            # Publish a message to a specific MQTT topic
            self.client.publish(topic, message)

    def get_data_from_topic(self, topic):
        # Retrieve and return the data associated with a specific MQTT topic
        if topic in self.received_messages:
            return self.received_messages[topic]
        else:
            return None  # Return None if the topic has not received any data


# Create an instance of the MQTTHandler class
mqtt_handler = MQTTHandler()
