#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.http.response import HttpResponse
from eAPI.models import *

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
STATUS_TEXT_CHOICES = {
    OK: 'OK',
    BAD_REQUEST: 'Неверный формат данных!',
    FORBIDDEN: 'Доступ запрещен!',
    NOT_FOUND: 'Страница не найдена',
    METHOD_NOT_ALLOWED: ''
}

NUMBER_OF_NEWS_DEFAULT = 20


def reformat_date(date):
    return date.strftime("%d %B %Y %H:%M:%S")


def return_user(user):
    response_user = {
        'users_id': user.pk,
        'last_name': user.last_name,
        'name': user.name
    }
    if user.vk_id:
        response_user.update({'vk_id': user.vk_id})
    else:
        response_user.update({'vk_id': 0})
    return response_user


def return_group(group):
    return {
        'groups_id': group.pk,
        'title': group.title
    }


def return_bill(bill):
    return {
        'bills_id': bill.pk,
        'title': bill.title,
        'sum': bill.sum,
        'is_deleted': bill.is_deleted
    }


def return_history(history):
    response_history = {
        'news_id': history.pk,
        'users_id_who': history.users_id_who.pk,
        'groups_id': history.groups_id.pk,
        'action': history.action,
        'action_datetime': reformat_date(history.action_datetime),
        'text_who': history.text_who,
        'text_description': history.text_description,
        'text_what_whom': history.text_what_whom
    }
    if history.users_id_who_say:
        response_history.update({'users_id_who_say': history.users_id_who_say.pk})
    if history.users_id_whom:
        response_history.update({'users_id_whom': history.users_id_whom.pk})
    if history.bills_id:
        response_history.update({'bills_id': history.bills_id.pk})
        edited_bills_id = history.bills_id.edited_bills_id
        if edited_bills_id:
            response_history.update({'edited_bills_id': edited_bills_id.pk})
    if history.debts_id:
        response_history.update({'debts_id': history.debts_id.pk})
    if history.text_who_say:
        response_history.update({'text_who_say': history.text_who_say})
    if history.text_say:
        response_history.update({'text_say': history.text_say})
    return response_history


def return_response(status, response_data=None):
    response = {'status': status, 'text': STATUS_TEXT_CHOICES[status]}
    if response_data:
        response.update({'response': response_data})
    return HttpResponse(json.dumps(response), content_type='application/json')


def return_login(user, friends_ids, is_new=1):
    users_id = user.pk
    response_data = {'users_id': users_id,
                     'access_token': user.access_token}
    if friends_ids:
        response_data.update({'friends_ids': friends_ids})
    if not is_new:
        # add added users - Friends
        friends = Friends.objects.filter(users_id=users_id, is_deleted=0)

        friends_data = {}
        i = 0
        for friend in friends:
            friends_data[i] = return_user(friend.users_id_added)
            i += 1
        response_data.update({'friends': friends_data})
        return return_user_debts(user, response_data)
    return return_response(OK, response_data)


def return_add_user(user, client_id):
    response_data = {'users_id': user.pk,
                     'id': client_id}
    return return_response(OK, response_data)


def return_groups(users_id):
    members = Members.objects.filter(users_id=users_id, is_deleted=0)

    response_data = {}
    i = 0
    for member in members:
        group = member.groups_id
        response_data[i] = {
            'groups_id': group.pk,
            'title': group.title,
            'update_datetime': reformat_date(group.update_datetime),
            'is_calculated': group.is_calculated
        }
        i += 1
    response_data = {'groups': response_data}
    return return_response(OK, response_data)


def return_add_groups(groups_id, history, client_id):
    response_data = {
        'groups_id': groups_id,
        'id': client_id,
        'history': return_history(history)
    }
    return return_response(OK, response_data)


def return_edit_groups(group, history=None):
    response_data = {
        'groups_id': group.pk
    }
    if history:
        response_data.update({'history': return_history(history)})
    return return_response(OK, response_data)


def return_members(group, history=None):
    members = Members.objects.filter(groups_id=group.pk, is_deleted=0)

    response_data = {}
    i = 0
    for member in members:
        response_data[i] = return_user(member.users_id)
        i += 1
    response_data = {
        'group': return_group(group),
        'members': response_data
    }
    if history:
        response_data.update({
            'history': return_history(history)
        })
    return return_response(OK, response_data)


def return_add_members(group, history=None):
    return return_members(group, history)


def return_remove_members(group, history=None):
    return return_members(group, history)


def return_groups_history(group, response_data=None, number_of_news=NUMBER_OF_NEWS_DEFAULT, news_id=None):
    if news_id:
        news = History.objects.filter(groups_id=group.pk, id__lt=news_id).order_by('-action_datetime')[:number_of_news]
    else:
        news = History.objects.filter(groups_id=group.pk).order_by('-action_datetime')[:number_of_news]

    if not response_data:
        response_data = {}
    history_data = {}
    i = 0
    for item in news:
        history_data[i] = return_history(item)
        i += 1

    response_data.update({
        'group': return_group(group),
        'history': history_data
    })
    return return_response(OK, response_data)


def return_add_bills(bill, client_id, history):
    response_data = {
        'bills_id': bill.pk,
        'id': client_id,
        'groups_id': bill.groups_id.pk,
        'history': return_history(history)
    }
    return return_response(OK, response_data)


def return_edit_bills(bill, history=None):
    response_data = {
        'bills_id': bill.pk,
        'edited_bills_id': bill.edited_bills_id.pk,
        'groups_id': bill.groups_id.pk,
    }
    if history:
        response_data.update({'history': return_history(history)})
    return return_response(OK, response_data)


def return_remove_bills(group, history):
    response_data = {
        'groups_id': group.pk,
        'history': return_history(history)
    }
    return return_response(OK, response_data)


def return_restore_bills(group, history):
    response_data = {
        'groups_id': group.pk,
        'history': return_history(history)
    }
    return return_response(OK, response_data)


def return_bills_details(bill):
    bills_details = BillsDetails.objects.filter(bills_id=bill.pk)

    response_data = {}
    i = 0
    for bills_detail in bills_details:
        response_data[i] = {
            'user': return_user(bills_detail.users_id),
            'debt_sum': bills_detail.debt_sum,
            'investment_sum': bills_detail.investment_sum
        }
        i += 1
    response_data = {
        'bill': return_bill(bill),
        'bills_details': response_data
    }
    return return_response(OK, response_data)


def return_user_debts(user, response_data=None):
    if not response_data:
        response_data = {}
    users_id = user.pk
    # Debts filter users_is_who
    debts = Debts.objects.filter(users_id_who=users_id, is_actual=1, is_deleted=0)

    response_data_who = {}
    debt_sum_who = i = 0
    for debt in debts:
        debt_sum = debt.sum
        response_data_who[i] = {
            'sum': debt_sum,
            'group': return_group(debt.groups_id)
        }
        user_whom = debt.users_id_whom
        if user_whom:
            response_data_who[i].update({'user': return_user(user_whom)})
        debt_sum_who += debt_sum
        i += 1
    response_data_who.update({'sum': debt_sum_who})

    # Debts filter users_is_whom
    debts = Debts.objects.filter(users_id_whom=users_id, is_actual=1, is_deleted=0)

    response_data_whom = {}
    debt_sum_whom = i = 0
    for debt in debts:
        debt_sum = debt.sum
        response_data_whom[i] = {
            'sum': debt_sum,
            'group': return_group(debt.groups_id)
        }
        user_who = debt.users_id_who
        if user_who:
            response_data_whom[i].update({'user': return_user(user_who)})
        debt_sum_whom += debt_sum
        i += 1
    response_data_whom.update({'sum': debt_sum_whom})

    response_data.update({
        'debts_who': response_data_who,
        'debts_whom': response_data_whom
    })
    return return_response(OK, response_data)


def return_debts(group, history=None):
    debts = Debts.objects.filter(groups_id=group.pk, is_actual=1)

    response_data = {}
    i = 0
    for debt in debts:
        response_data[i] = {
            'debts_id': debt.pk,
            'user_who': return_user(debt.users_id_who),
            'user_whom': return_user(debt.users_id_whom),
            'sum': debt.sum,
            'is_deleted': debt.is_deleted
        }
        i += 1
    response_data = {
        'group': return_group(group),
        'debts': response_data
    }
    if history:
        response_data.update({
            'history': return_history(history)
        })
    return return_response(OK, response_data)


def return_edit_debts(group, history=None):
    response_data = {'groups_id': group.pk}
    if not history:
        return return_response(OK, response_data)
    history_data = {}
    i = 0
    for item in history:
        history_data[i] = return_history(item)
        i += 1
    response_data.update({
        'history': history_data
    })
    return return_response(OK, response_data)


def return_debts_details(member):
    groups_id = member.groups_id.pk
    bills_details = BillsDetails.objects.filter(groups_id=groups_id, users_id=member.users_id.pk, is_actual=1,
                                                is_deleted=0)
    response_data = {}
    i = 0
    for bills_detail in bills_details:
        response_data[i] = {
            'bill': return_bill(bills_detail.bills_id),
            'debt_sum': bills_detail.debt_sum,
            'investment_sum': bills_detail.investment_sum,
            'sum': bills_detail.investment_sum - bills_detail.debt_sum  # не долги, а вложения
        }
        i += 1
    response_data = {
        'groups_id': groups_id,
        'debts_details': response_data
    }
    return return_response(OK, response_data)
