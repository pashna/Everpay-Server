# coding=utf-8
from gcm.models import Device
from eAPI.models import *

ACTION = 'action'
GROUPS_ID = 'groups_id'
BILLS_ID = 'bills_id'
TEXT = 'text'
YOU = 'Вас'
YOU_WHO = 'Вы'
YOU_WHOM = 'Вам'


def get_in_group(title):
    return ' в группе "' + title + '"'


def get_he_she(sex):
    if sex == MAN:
        return 'он'
    else:
        return 'она'


def get_him_her(sex):
    if sex == MAN:
        return 'ему'
    else:
        return 'ей'


text_edit_debts_you = HISTORY_ACTION_CHOICES[EDIT_DEBTS][1]
text_edit_debts_you = text_edit_debts_you.split(' ')
text_edit_debts_you[0] += 'и'
text_edit_debts_you = " ".join(text_edit_debts_you)


def change_text_edit_debts_you(text):
    text = text.split(' ')
    if len(text) == 2:
        return text_edit_debts_you
    else:
        return 'не ' + text_edit_debts_you


def send_message_groups(action, history):
    # всем участникам группы, кроме инициатора действия
    groups_id = history.groups_id.pk
    data = {
        ACTION: action,
        GROUPS_ID: groups_id,
        TEXT: history.text_who.encode('utf8') + ' ' + history.text_description + ' ' + history.text_what_whom.encode(
            'utf8')
    }
    members = Members.objects.filter(groups_id=groups_id, is_deleted=0).exclude(users_id=history.users_id_who.pk)
    for member in members:
        Device.objects.filter(users_id=member.users_id).send_message(data)


def send_message_add_members(history, users_id):
    # добавленному участнику
    data = {
        ACTION: ADD_MEMBERS,
        GROUPS_ID: history.groups_id.pk,
        TEXT: history.text_who.encode(
            'utf8') + ' ' + history.text_description + ' ' + YOU + ' в группу "' + history.groups_id.title.encode(
            'utf8') + '"'
    }
    Device.objects.filter(users_id=users_id).send_message(data)


# надо ли ???
def send_message_remove_members(history, users_id):
    # исключенному участнику
    data = {
        ACTION: REMOVE_MEMBERS,
        GROUPS_ID: history.groups_id.pk,
        TEXT: history.text_who.encode(
            'utf8') + ' ' + history.text_description + ' ' + YOU + ' из группы "' + history.groups_id.title.encode(
            'utf8') + '"'
    }
    Device.objects.filter(users_id=users_id).send_message(data)


def send_message_bills(action, history, bills_details):  # action = ADD_BILLS or EDIT_BILLS
    # всем участникам счета, кроме создателя / изменяющего
    data = {
        ACTION: action,
        GROUPS_ID: history.groups_id.pk,
        BILLS_ID: history.bills_id.pk,
        TEXT: history.text_who.encode('utf8') + ' ' + history.text_description + ' ' + history.text_what_whom.encode(
            'utf8') + get_in_group(history.groups_id.title.encode('utf8'))
    }
    users_id_who = history.users_id_who.pk
    for key in bills_details:
        users_id = bills_details[key]['users_id']
        if users_id != users_id_who:
            Device.objects.filter(users_id=users_id).send_message(data)


def send_message_edit_debts(history):
    # тому, кто отдал и кому отдали, если не совпадает с тем, кто сказал
    text_say = history.text_who_say.encode('utf8') + ' ' + history.text_say + ' '
    text_in_group = get_in_group(history.groups_id.title.encode('utf8'))

    users_id_who_say = history.users_id_who_say.pk
    users_id_who = history.users_id_who.pk
    users_id_whom = history.users_id_whom.pk
    users_sex = history.users_id_who_say.sex
    text_who = ''
    text_whom = ''
    # кто отдал = кто сказал
    if users_id_who_say == users_id_who:
        text_whom = get_he_she(users_sex) + ' ' + history.text_description + ' ' + YOU_WHOM
    # кому отдали = кто сказал
    elif users_id_who_say == users_id_whom:
        text_who = YOU_WHO + ' ' + change_text_edit_debts_you(history.text_description) + ' ' + get_him_her(users_sex)
    else:
        text_who = YOU_WHO + ' ' + change_text_edit_debts_you(
            history.text_description) + ' ' + history.text_what_whom.encode('utf8')
        text_whom = history.text_who.encode('utf8') + ' ' + history.text_description + ' ' + YOU_WHOM

    data = {
        ACTION: EDIT_DEBTS,
        GROUPS_ID: history.groups_id.pk,
    }
    if text_who:
        data_who = data
        data_who.update({TEXT: text_say + text_who + text_in_group})
        Device.objects.filter(users_id=users_id_who).send_message(data_who)
    if text_whom:
        data_whom = data
        data_whom.update({TEXT: text_say + text_whom + text_in_group})
        Device.objects.filter(users_id=users_id_whom).send_message(data_whom)


def send_message_remind_about_debts(member):
    users_id = member.users_id.pk
    group = member.groups_id
    groups_id = group.pk
    data = {
        ACTION: REMIND_ABOUT_DEBTS,
        GROUPS_ID: groups_id,
        TEXT: 'У Вас есть незакрытые счета в группе "' + group.title.encode('utf8') + '"'
    }
    # Debts filter users_is_who
    debts = Debts.objects.filter(users_id_who=users_id, groups_id=groups_id, is_actual=1, is_deleted=0)
    for debt in debts:
        Device.objects.filter(users_id=debt.users_id_whom).send_message(data)

    # Debts filter users_is_whom
    debts = Debts.objects.filter(users_id_whom=users_id, groups_id=groups_id, is_actual=1, is_deleted=0)
    for debt in debts:
        Device.objects.filter(users_id=debt.users_id_who).send_message(data)