#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.forms import *
from eAPI.models import *


class UsersForm(ModelForm):
    class Meta:
        model = Users
        exclude = ['access_token', 'is_deleted']


class UsersAddForm(ModelForm):
    class Meta:
        model = Users
        exclude = ['vk_id', 'access_token', 'is_deleted']


class FriendsForm(ModelForm):
    class Meta:
        model = Friends
        exclude = ['is_deleted']


class GroupsForm(ModelForm):
    class Meta:
        model = Groups
        exclude = ['creation_datetime', 'update_datetime', 'is_calculated', 'is_deleted']


class MembersForm(ModelForm):
    class Meta:
        model = Members
        exclude = ['is_deleted']


class BillsForm(ModelForm):
    class Meta:
        model = Bills
        exclude = ['sum', 'is_actual', 'edited_bills_id', 'creation_datetime', 'is_deleted']


class BillsEditForm(ModelForm):
    class Meta:
        model = Bills
        exclude = ['sum', 'is_actual', 'creation_datetime', 'is_deleted']


class BillsDetailsForm(ModelForm):
    class Meta:
        model = BillsDetails
        exclude = ['is_actual', 'is_deleted']


class DebtsForm(ModelForm):
    class Meta:
        model = Debts
        exclude = ['is_actual', 'is_deleted']


class DebtsWhoForm(ModelForm):
    class Meta:
        model = Debts
        exclude = ['users_id_whom', 'is_actual', 'is_deleted']


class DebtsWhomForm(ModelForm):
    class Meta:
        model = Debts
        exclude = ['users_id_who', 'is_actual', 'is_deleted']

