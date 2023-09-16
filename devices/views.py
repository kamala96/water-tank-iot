from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TankOwner


class TankOwnerListView(ListView):
    model = TankOwner
    template_name = 'tank_owner_list.html'
    context_object_name = 'tank_owners'


class TankOwnerCreateView(CreateView):
    model = TankOwner
    template_name = 'tank_owner_form.html'
    fields = ['name', 'email', 'phone']


class TankOwnerUpdateView(UpdateView):
    model = TankOwner
    template_name = 'tank_owner_form.html'
    fields = ['name', 'email', 'phone']


class TankOwnerDeleteView(DeleteView):
    model = TankOwner
    template_name = 'tank_owner_confirm_delete.html'
    success_url = '/tank-owners/'
