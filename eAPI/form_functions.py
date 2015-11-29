#!/usr/bin/python
# -*- coding: utf-8 -*-
from eAPI.models import *
from datetime import datetime
from gcm.models import Device


def save_users_form(form):
    vk_id = form.cleaned_data["vk_id"]
    try:
        user = Users.objects.get(vk_id=vk_id)
    except Users.DoesNotExist:
        # signup
        last_name = form.cleaned_data["last_name"]
        name = form.cleaned_data["name"]
        sex = form.cleaned_data["sex"]
        new_user = Users.objects.create(vk_id=vk_id,
                                        last_name=last_name,
                                        name=name,
                                        sex=sex)
        return new_user, True
    # signin
    return user, False


def save_users_add_form(form):
    last_name = form.cleaned_data["last_name"]
    name = form.cleaned_data["name"]
    sex = form.cleaned_data["sex"]
    return Users.objects.create(last_name=last_name,
                                name=name,
                                sex=sex)


def save_friends_form(form):
    users_id = form.cleaned_data["users_id"]
    users_id_added = form.cleaned_data["users_id_added"]
    Friends.objects.create(users_id=users_id,
                           users_id_added=users_id_added)


def save_groups_form(form):
    datetime_now = datetime.now()
    users_id = form.cleaned_data["users_id"]
    title = form.cleaned_data["title"]
    return Groups.objects.create(users_id=users_id,
                                 title=title,
                                 creation_datetime=datetime_now,
                                 update_datetime=datetime_now)


def save_members_form(form):
    users_id = form.cleaned_data["users_id"]
    groups_id = form.cleaned_data["groups_id"]
    return Members.objects.create(users_id=users_id,
                                  groups_id=groups_id)


def save_bills_form(form):
    users_id = form.cleaned_data["users_id"]
    groups_id = form.cleaned_data["groups_id"]
    title = form.cleaned_data["title"]
    return Bills.objects.create(users_id=users_id,
                                groups_id=groups_id,
                                title=title,
                                creation_datetime=datetime.now())


def save_bills_edit_form(form):
    users_id = form.cleaned_data["users_id"]
    groups_id = form.cleaned_data["groups_id"]
    title = form.cleaned_data["title"]
    edited_bills_id = form.cleaned_data["edited_bills_id"]
    return Bills.objects.create(users_id=users_id,
                                groups_id=groups_id,
                                title=title,
                                edited_bills_id=edited_bills_id,
                                creation_datetime=datetime.now())


def save_bills_details_form(form):
    groups_id = form.cleaned_data["groups_id"]
    bills_id = form.cleaned_data["bills_id"]
    users_id = form.cleaned_data["users_id"]
    debt_sum = form.cleaned_data["debt_sum"]
    investment_sum = form.cleaned_data["investment_sum"]
    BillsDetails.objects.create(groups_id=groups_id,
                                bills_id=bills_id,
                                users_id=users_id,
                                debt_sum=debt_sum,
                                investment_sum=investment_sum)
    return debt_sum, investment_sum


def save_debts_form(form):
    users_id_who = form.cleaned_data["users_id_who"]
    users_id_whom = form.cleaned_data["users_id_whom"]
    groups_id = form.cleaned_data["groups_id"]
    debts_sum = form.cleaned_data["sum"]
    Debts.objects.create(users_id_who=users_id_who,
                         users_id_whom=users_id_whom,
                         groups_id=groups_id,
                         sum=debts_sum)


def save_debts_who_form(form):
    users_id_who = form.cleaned_data["users_id_who"]
    groups_id = form.cleaned_data["groups_id"]
    debts_sum = form.cleaned_data["sum"]
    Debts.objects.create(users_id_who=users_id_who,
                         groups_id=groups_id,
                         sum=debts_sum)


def save_debts_whom_form(form):
    users_id_whom = form.cleaned_data["users_id_whom"]
    groups_id = form.cleaned_data["groups_id"]
    debts_sum = form.cleaned_data["sum"]
    Debts.objects.create(users_id_whom=users_id_whom,
                         groups_id=groups_id,
                         sum=debts_sum)


def save_register_device_form(form):
    reg_id = form.cleaned_data["reg_id"]
    users_id = form.cleaned_data["users_id"]
    Device.objects.create(reg_id=reg_id,
                          users_id=users_id)