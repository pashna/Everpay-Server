#!/usr/bin/python
# -*- coding: utf-8 -*-
from eAPI.models import *
from datetime import datetime
from eAPI.pymorphy2_functions import to_accs, to_datv


def change_text_with_sex(text, user):
    if user.sex == MAN:
        return text
    text = text.split(' ')
    text[0] += 'а'
    return " ".join(text)


def save_history_add_groups(user, group):
    datetime_now = datetime.now()
    group.update_datetime = datetime_now
    group.save()
    return History.objects.create(users_id_who=user,
                                  groups_id=group,
                                  action=ADD_GROUPS,
                                  action_datetime=datetime_now,
                                  text_who=user.name + ' ' + user.last_name,
                                  text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[ADD_GROUPS][1], user),
                                  text_what_whom='"' + group.title + '"')


def save_history_edit_groups(user, group):
    datetime_now = datetime.now()
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     action=EDIT_GROUPS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[EDIT_GROUPS][1],
                                                                           user),
                                     text_what_whom='"' + group.title + '"')
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_add_members(user, member):
    datetime_now = datetime.now()
    group = member.groups_id
    user_whom = member.users_id
    history = History.objects.create(users_id_who=user,
                                     users_id_whom=user_whom,
                                     groups_id=member.groups_id,
                                     action=ADD_MEMBERS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[ADD_MEMBERS][1],
                                                                           user),
                                     text_what_whom=to_accs(user_whom.name + ' ' + user_whom.last_name))
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_remove_members(user, member):
    datetime_now = datetime.now()
    group = member.groups_id
    user_whom = member.users_id
    history = History.objects.create(users_id_who=user,
                                     users_id_whom=user_whom,
                                     groups_id=group,
                                     action=REMOVE_MEMBERS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[REMOVE_MEMBERS][1],
                                                                           user),
                                     text_what_whom=to_accs(user_whom.name + ' ' + user_whom.last_name))
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_add_bills(user, bill):
    datetime_now = datetime.now()
    group = bill.groups_id
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     bills_id=bill,
                                     action=ADD_BILLS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[ADD_BILLS][1], user),
                                     text_what_whom='"' + bill.title + '"')
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_edit_bills(user, bill, prev_title):
    datetime_now = datetime.now()
    group = bill.groups_id
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     bills_id=bill,
                                     action=EDIT_BILLS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[EDIT_BILLS][1], user),
                                     text_what_whom='"' + prev_title + '"')  # название счета до редактирования
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_remove_bills(user, bill):
    datetime_now = datetime.now()
    group = bill.groups_id
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     bills_id=bill,
                                     action=REMOVE_BILLS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[REMOVE_BILLS][1],
                                                                           user),
                                     text_what_whom='"' + bill.title + '"')
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_restore_bills(user, bill):
    datetime_now = datetime.now()
    group = bill.groups_id
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     bills_id=bill,
                                     action=RESTORE_BILLS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[RESTORE_BILLS][1],
                                                                           user),
                                     text_what_whom='"' + bill.title + '"')
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_add_debts(user, group):
    datetime_now = datetime.now()
    history = History.objects.create(users_id_who=user,
                                     groups_id=group,
                                     action=ADD_DEBTS,
                                     action_datetime=datetime_now,
                                     text_who=user.name + ' ' + user.last_name,
                                     text_description=change_text_with_sex(HISTORY_ACTION_CHOICES[ADD_DEBTS][1], user),
                                     text_what_whom='"' + group.title + '"')
    group.update_datetime = datetime_now
    group.save()
    return history


def save_history_edit_debts(user, debt):
    datetime_now = datetime.now()
    group = debt.groups_id
    user_who = debt.users_id_who
    user_whom = debt.users_id_whom
    text_description = change_text_with_sex(HISTORY_ACTION_CHOICES[EDIT_DEBTS][1], user_who)
    if debt.is_deleted == 0:
        text_description = 'не ' + text_description
    history = History.objects.create(users_id_who_say=user,
                                     users_id_who=user_who,
                                     users_id_whom=user_whom,
                                     groups_id=group,
                                     debts_id=debt,
                                     action=EDIT_DEBTS,
                                     action_datetime=datetime_now,
                                     text_who_say=user.name + ' ' + user.last_name,
                                     text_say=change_text_with_sex(SAY, user) + WHAT,
                                     text_who=user_who.name + ' ' + user_who.last_name,
                                     text_description=text_description,
                                     text_what_whom=to_datv(user_whom.name + ' ' + user_whom.last_name))
    group.update_datetime = datetime_now
    group.save()
    return history
