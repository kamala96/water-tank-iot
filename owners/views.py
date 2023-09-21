from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import json
from devices.models import WaterTankSensor

from owners.models import TankOwner
from owners.mqtt_handler import mqtt_handler
# from django.contrib.auth.mixins import LoginRequiredMixin


from .forms import LoginForm

# Create your views here.


def index(request):
    return render(request, 'index.html')


def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or dashboard
                return redirect('account-home')
            else:
                # Handle invalid login credentials
                # You can add an error message to the form if needed
                form.add_error(None, 'Invalid login credentials')

    else:
        form = LoginForm()

    return render(request, 'sign_in.html', {'form': form})


@login_required
def account_home(request):
    # Retrieve the logged-in user's TankOwner instance
    try:
        tank_owner = TankOwner.objects.get(user=request.user)

        # Retrieve MQTT data for the user's Waterlevel Sensors and Water Tanks
        water_tanks_obj = WaterTankSensor.objects.filter(
            processor__owner=tank_owner)

        water_tanks = []

        for tank in water_tanks_obj:
            pump_status = tank.get_full_topic()

            tank_dict = {
                'id': tank.mqtt_topic,
                'name': tank.name,
                'percentage': tank.calculate_percentage(),
                'pump_status': tank.get_pump_status(),
                'topic': {
                    'pump_status': tank.get_full_topic(),
                    'pump_mode': 'NIT/JIU/LOJJ',
                }
            }
            water_tanks.append(tank_dict)

        # Define the MQTT topics you want to subscribe to
        # mqtt_topics = [
        #     "topic1",
        #     "topic2",
        #     # Add more topics as needed
        # ]

        # Subscribe to MQTT topics
        # for topic in mqtt_topics:
        #     mqtt_handler.subscribe_topic(topic)

        # Retrieve MQTT data for the subscribed topics
        # mqtt_data = {}
        # for topic in mqtt_topics:
        #     data = mqtt_handler.get_data_from_topic(topic)
        #     mqtt_data[topic] = data

        # print(mqtt_data)

        # data = mqtt_handler.get_data_from_topic("NIT/home/channel/45")
        # print(data)

        # If wanting to publish
        # request_data = json.loads(request.body)
        # rc, mid = mqtt_handler.publish(request_data['topic'], request_data['msg'])
        # return JsonResponse({'code': rc})

        context = {
            'owner_topic': tank_owner.mqtt_topic,
            'water_tanks': water_tanks,
        }

    except TankOwner.DoesNotExist:
        pass

    return render(request, 'account_home.html', context)
