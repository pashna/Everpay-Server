#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import string
from eAPI.form import *
from eAPI.form_functions import *
from eAPI.models import *

LENGTH_OF_ACCESS_TOKEN_DEFAULT = 50


def clear_groups(group):
    Members.objects.filter(groups_id=group).delete()
    group.delete()


def clear_bills(bill, bills_details_prev=None):
    BillsDetails.objects.filter(bills_id=bill).delete()
    bill.delete()
    # if edit bills
    if bills_details_prev:
        for bills_detail in bills_details_prev:
            bills_detail.is_deleted = 0
            bills_detail.save()


def update_debt(debt, debts_sum):
    if debts_sum > 0:
        debt.sum = debts_sum
        debt.save()
    elif debts_sum < 0:
        if debt.users_id_who:
            debt.users_id_whom = debt.users_id_who
            debt.users_id_who = None
        else:
            debt.users_id_who = debt.users_id_whom
            debt.users_id_whom = None
        debt.sum = -debts_sum
        debt.save()
    else:
        debt.is_actual = 0
        debt.save()


def make_debts_not_actual(groups_id):
    debts = Debts.objects.filter(groups_id=groups_id, is_actual=1)

    debts_history = {}
    for debt in debts:
        user_who = debt.users_id_who
        if user_who:
            debts_history.update({user_who.pk: debt.sum})
        else:
            debts_history.update({debt.users_id_whom.pk: -debt.sum})
        debt.is_actual = 0
        debt.save()

    return debts_history


def make_debts(groups_id, debts_history):
    for key in debts_history:
        debts_sum = debts_history[key]
        form_data = {'groups_id': groups_id}
        if debts_sum > 0:
            form_data.update({'users_id_who': key, 'sum': debts_sum})
            form = DebtsWhoForm(form_data)
            if form.is_valid():
                save_debts_who_form(form)
        elif debts_sum < 0:
            form_data.update({'users_id_whom': key, 'sum': -debts_sum})
            form = DebtsWhomForm(form_data)
            if form.is_valid():
                save_debts_whom_form(form)


def make_debts_actual(groups_id, debts_history):
    debts = Debts.objects.filter(groups_id=groups_id, is_actual=1)

    for debt in debts:
        user_who = debt.users_id_who
        if user_who:
            users_id_who = user_who.pk
            if users_id_who in debts_history:
                update_debt(debt, debt.sum + debts_history[users_id_who])
                del debts_history[users_id_who]
        else:
            users_id_whom = debt.users_id_whom.pk
            if users_id_whom in debts_history:
                update_debt(debt, debt.sum - debts_history[users_id_whom])
                del debts_history[users_id_whom]

    make_debts(groups_id, debts_history)


def make_user_debts_not_actual(groups_id, debts_history):
    debts = Debts.objects.filter(groups_id=groups_id, is_actual=1)

    for debt in debts:
        if debt.is_deleted == 0:
            users_id_who = debt.users_id_who.pk
            debts_sum = debt.sum
            if users_id_who in debts_history:
                debts_history[users_id_who] += debts_sum
            else:
                debts_history.update({users_id_who: debts_sum})

            users_id_whom = debt.users_id_whom.pk
            if users_id_whom in debts_history:
                debts_history[users_id_whom] -= debts_sum
            else:
                debts_history.update({users_id_whom: -debts_sum})

        debt.is_actual = 0
        debt.save()


def make_user_debts_actual(groups_id, debts_history):
    while debts_history:
        users_id_min = min(debts_history, key=debts_history.get)
        users_id_max = max(debts_history, key=debts_history.get)
        debt_min = debts_history[users_id_min]
        debt_max = debts_history[users_id_max]
        debts_diff = debt_max + debt_min
        if debts_diff > 0:
            debts_history[users_id_max] = debts_diff
            debts_sum = -debt_min
            del debts_history[users_id_min]
        elif debts_diff < 0:
            debts_history[users_id_min] = debts_diff
            debts_sum = debt_max
            del debts_history[users_id_max]
        else:
            debts_sum = debt_max
            del debts_history[users_id_min]
            del debts_history[users_id_max]
        form_data = {'users_id_who': users_id_max,
                     'users_id_whom': users_id_min,
                     'groups_id': groups_id,
                     'sum': debts_sum}
        form = DebtsForm(form_data)
        if form.is_valid():
            # Debts create
            save_debts_form(form)


def generate_debts(group, debts_history=None):
    groups_id = group.pk
    if group.is_calculated:
        make_user_debts_not_actual(groups_id, debts_history)
        make_debts(groups_id, debts_history)
        group.is_calculated = 0
        group.save()
    else:
        make_debts_actual(groups_id, debts_history)


def generate_user_debts(group):
    debts_history = make_debts_not_actual(group.pk)
    make_user_debts_actual(group.pk, debts_history)
    group.is_calculated = 1
    group.save()


def generate_access_token(length=LENGTH_OF_ACCESS_TOKEN_DEFAULT,
                          chars=string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def make_bills_details_not_actual(debt):
    bills_details = BillsDetails.objects.filter(groups_id=debt.groups_id, users_id=debt.users_id_who.pk, is_actual=1,
                                                is_deleted=0)
    for bills_detail in bills_details:
        bills_detail.is_actual = 0
        bills_detail.save()


def make_bills_details_actual(debt):
    bills_details = BillsDetails.objects.filter(groups_id=debt.groups_id, users_id=debt.users_id_who.pk, is_actual=0,
                                                is_deleted=0).order_by('-bills_id__creation_datetime')
    sum = 0
    debt_sum = debt.sum
    for bills_detail in bills_details:
        if sum != debt_sum:
            sum += bills_detail.debts_sum - bills_detail.investment_sum
            bills_detail.is_actual = 1
            bills_detail.save()
