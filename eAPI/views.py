#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from eAPI.functions import *
from eAPI.gcm_functions import *
from eAPI.history_functions import *
from eAPI.return_functions import *
from eAPI.form import *
from gcm.forms import *

LENGTH_OF_ACCESS_TOKEN_MIN = LENGTH_OF_ACCESS_TOKEN_DEFAULT
LENGTH_OF_ACCESS_TOKEN_MAX = 100


def login(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        if 'user' not in request_data:
            return return_response(BAD_REQUEST)

        user = request_data['user']

        keys = ['vk_id', 'last_name', 'name', 'sex']
        for key in keys:
            if key not in user:
                return return_response(BAD_REQUEST)

        form = UsersForm(user)

        if form.is_valid():
            # Users create
            new_user, is_new = save_users_form(form)
            if new_user is None:
                return return_response(FORBIDDEN)
            friends_ids = {}
            if 'friends' in request_data:
                friends = request_data['friends']
                for friends_key in friends:
                    friend = friends[friends_key]
                    keys = ['vk_id', 'last_name', 'name', 'sex']
                    for key in keys:
                        if key not in friend:
                            return return_response(BAD_REQUEST)

                    form = UsersForm(friend)
                    if form.is_valid():
                        # Users create
                        user_friend, is_new_friend = save_users_form(form)
                        friends_ids.update({friends_key: user_friend.pk})
                    else:
                        return return_response(BAD_REQUEST)
            # generate access token
            new_user.access_token = generate_access_token(
                randint(LENGTH_OF_ACCESS_TOKEN_MIN, LENGTH_OF_ACCESS_TOKEN_MAX))
            new_user.save()

            if is_new:
                return return_login(new_user, friends_ids)
            return return_login(new_user, friends_ids, 0)
        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def logout(request):
    if request.method == 'POST':
        # JSON validating
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        # data validating
        keys = ['users_id', 'access_token']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        user.access_token = ""
        user.save()

        return return_response(OK)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def add_users(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'user', 'id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        access_token = request_data['access_token']
        client_id = request_data['id']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        user = request_data['user']
        keys = ['last_name', 'name', 'sex']
        for key in keys:
            if key not in user:
                return return_response(BAD_REQUEST)

        form = UsersAddForm(user)
        if form.is_valid():
            # Users create
            new_user = save_users_add_form(form)
            # Friends create
            form_data = {'users_id': users_id, 'users_id_added': new_user.pk}
            form = FriendsForm(form_data)
            if form.is_valid():
                save_friends_form(form)
            else:
                return return_response(BAD_REQUEST)
        else:
            return return_response(BAD_REQUEST)

        return return_add_user(new_user, client_id)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_groups(request):
    if request.method == 'GET':

        if 'users_id' not in request.GET:
            return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
        except ValueError:
            return return_response(BAD_REQUEST)

        # Users get
        try:
            Users.objects.get(id=users_id)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        return return_groups(users_id)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def add_groups(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'title', 'users_id_members', 'id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        access_token = request_data['access_token']
        client_id = request_data['id']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        form = GroupsForm(request_data)
        if form.is_valid():
            # Groups create
            new_group = save_groups_form(form)

            # Members create
            members = request_data['users_id_members']
            for key in members:
                form_data = {'groups_id': new_group.pk, 'users_id': members[key]}
                form = MembersForm(form_data)
                if form.is_valid():
                    save_members_form(form)
                else:
                    clear_groups(new_group)
                    return return_response(BAD_REQUEST)

            history = save_history_add_groups(user, new_group)
            send_message_groups(ADD_GROUPS, history)

            return return_add_groups(new_group.pk, history, client_id)
        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def edit_groups(request):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'title']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        group = member.groups_id

        # Groups update
        form = GroupsForm(request_data)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if group.title == title:
                # Не изменял название группы --> не надо писать новость
                return return_edit_groups(group)

            group.title = title
            group.save()

            history = save_history_edit_groups(user, group)
            send_message_groups(EDIT_GROUPS, history)

            return return_edit_groups(group, history)
        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_members(request):
    if request.method == 'GET':
        keys = ['users_id', 'groups_id']
        for key in keys:
            if key not in request.GET:
                return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
            groups_id = int(request.GET['groups_id'])
        except ValueError:
            return return_response(BAD_REQUEST)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        return return_members(member.groups_id)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def add_members(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'users_id_whom']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['users_id_whom'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        users_id_whom = request_data['users_id_whom']

        # Members get
        try:
            member = Members.objects.get(users_id=users_id_whom, groups_id=groups_id)

            if member.is_deleted:
                member.is_deleted = 0
                member.save()

                history = save_history_add_members(user, member)
                send_message_add_members(history, member.users_id.pk)

                return return_add_members(member.groups_id, history)

            # Не добавил участника --> не надо писать новость
            return return_add_members(member.groups_id)
        except Members.DoesNotExist:
            form_data = {'groups_id': groups_id, 'users_id': users_id_whom}
            form = MembersForm(form_data)
            if form.is_valid():
                new_member = save_members_form(form)

                history = save_history_add_members(user, new_member)
                send_message_add_members(history, new_member.users_id.pk)

                return return_add_members(new_member.groups_id, history)
            else:
                return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def remove_members(request):
    if request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'users_id_whom']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['users_id_whom'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        users_id_whom = request_data['users_id_whom']

        # Members get
        try:
            member = Members.objects.get(users_id=users_id_whom, groups_id=groups_id)
        except Members.DoesNotExist:
            return return_response(BAD_REQUEST)

        if member.is_deleted == 0:
            member.is_deleted = 1
            member.save()

            history = save_history_remove_members(user, member)
            return return_remove_members(member.groups_id, history)

        # Не удалил участника --> не надо писать новость
        return return_remove_members(member.groups_id)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_groups_history(request):
    if request.method == 'GET':
        keys = ['users_id', 'groups_id']
        for key in keys:
            if key not in request.GET:
                return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
            groups_id = int(request.GET['groups_id'])
            if 'number' in request.GET:
                number_of_news = int(request.GET['number'])
            else:
                number_of_news = NUMBER_OF_NEWS_DEFAULT
            if 'news_id' in request.GET:
                news_id = int(request.GET['news_id'])
            else:
                news_id = None
        except ValueError:
            return return_response(BAD_REQUEST)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)
        return return_groups_history(member.groups_id, number_of_news=number_of_news, news_id=news_id)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def add_bills(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'title', 'bills_details', 'id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']
        client_id = request_data['id']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        # Bills create
        form = BillsForm(request_data)

        if form.is_valid():
            new_bill = save_bills_form(form)

            # BillsDetails create
            debt_sum = investment_sum = 0
            group = new_bill.groups_id

            bills_details = request_data['bills_details']
            debts_history = {}
            keys = ['users_id', 'debt_sum', 'investment_sum']
            for bills_details_key in bills_details:
                for key in keys:
                    if key not in bills_details[bills_details_key]:
                        clear_bills(new_bill)
                        return return_response(BAD_REQUEST)

                bills_details[bills_details_key].update({'groups_id': groups_id})
                bills_details[bills_details_key].update({'bills_id': new_bill.pk})
                form = BillsDetailsForm(bills_details[bills_details_key])
                if form.is_valid():
                    # BillsDetails create
                    debt_sum_cur, investment_sum_cur = save_bills_details_form(form)
                    debt_sum += debt_sum_cur
                    investment_sum += investment_sum_cur

                    debts_history.update(
                        {bills_details[bills_details_key]['users_id']: debt_sum_cur - investment_sum_cur})
                else:
                    clear_bills(new_bill)
                    return return_response(BAD_REQUEST)

            if debt_sum == investment_sum:
                new_bill.sum = debt_sum
                new_bill.is_actual = 1
                new_bill.save()
            else:
                clear_bills(new_bill)
                return return_response(BAD_REQUEST)

            history = save_history_add_bills(user, new_bill)

            send_message_bills(ADD_BILLS, history, bills_details)

            generate_debts(group, debts_history)

            return return_add_bills(new_bill, client_id, history)
        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def edit_bills(request):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'edited_bills_id', 'title', 'bills_details']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['edited_bills_id'], int):
            return return_response(BAD_REQUEST)

        is_edited_many_times = 0
        if 'bills_id' in request_data:
            is_edited_many_times = 1
            if not isinstance(request_data['bills_id'], int):
                return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        edited_bills_id = request_data['edited_bills_id']
        access_token = request_data['access_token']
        bills_id = None
        if is_edited_many_times:
            bills_id = request_data['bills_id']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        # Bills get
        try:
            if is_edited_many_times:
                cur_bill = Bills.objects.get(id=bills_id, groups_id=groups_id, is_actual=1,
                                             edited_bills_id=edited_bills_id, is_deleted=0)
            else:
                cur_bill = Bills.objects.get(id=edited_bills_id, groups_id=groups_id, is_actual=1, is_deleted=0)
        except Bills.DoesNotExist:
            return return_response(BAD_REQUEST)

        is_edited = 0
        # Bills create
        form = BillsEditForm(request_data)

        if form.is_valid():
            new_bill = save_bills_edit_form(form)
            prev_title = cur_bill.title
            if new_bill.title != prev_title:
                is_edited = 1

            if is_edited_many_times:
                bills_details_prev = BillsDetails.objects.filter(bills_id=bills_id, is_deleted=0)
            else:
                bills_details_prev = BillsDetails.objects.filter(bills_id=edited_bills_id, is_deleted=0)

            debts_history = {}
            for bills_detail in bills_details_prev:
                users_id = bills_detail.users_id.pk

                debts_history.update({users_id: {'debt_sum': bills_detail.debt_sum,
                                                 'investment_sum': bills_detail.investment_sum}})
                bills_detail.is_deleted = 1
                bills_detail.save()

            debt_sum = investment_sum = 0

            bills_details = request_data['bills_details']
            keys = ['users_id', 'debt_sum', 'investment_sum']
            for bills_details_key in bills_details:
                for key in keys:
                    if key not in bills_details[bills_details_key]:
                        clear_bills(new_bill, bills_details_prev)
                        return return_response(BAD_REQUEST)

                bills_details[bills_details_key].update({'groups_id': groups_id})
                bills_details[bills_details_key].update({'bills_id': new_bill.pk})
                form = BillsDetailsForm(bills_details[bills_details_key])
                if form.is_valid():
                    # BillsDetails create
                    debt_sum_cur, investment_sum_cur = save_bills_details_form(form)
                    debt_sum += debt_sum_cur
                    investment_sum += investment_sum_cur

                    users_id = bills_details[bills_details_key]['users_id']
                    if users_id in debts_history:
                        # BillsDetails updated
                        debt_sum_prev = debts_history[users_id]['debt_sum']
                        investment_sum_prev = debts_history[users_id]['investment_sum']
                        if debt_sum_prev != debt_sum_cur or investment_sum_prev != investment_sum_cur:
                            is_edited = 1
                        debts_history.update({users_id: (debt_sum_cur - debt_sum_prev) -
                                                        (investment_sum_cur - investment_sum_prev)})
                    else:
                        # BillsDetails created
                        is_edited = 1
                        debts_history.update({users_id: debt_sum_cur - investment_sum_cur})
                else:
                    clear_bills(new_bill, bills_details_prev)
                    return return_response(BAD_REQUEST)

            if debt_sum == investment_sum:
                new_bill.sum = debt_sum
                new_bill.is_actual = 1
                new_bill.save()
            else:
                clear_bills(new_bill, bills_details_prev)
                return return_response(BAD_REQUEST)

            for debts_history_key in debts_history:
                debt_history = debts_history[debts_history_key]
                # BillsDetails deleted
                if hasattr(debt_history, '__iter__'):
                    is_edited = 1
                    debts_history.update({debts_history_key: debt_history['investment_sum'] - debt_history['debt_sum']})

            group = cur_bill.groups_id
            if is_edited:
                cur_bill.is_actual = 0
                cur_bill.save()
                history = save_history_edit_bills(user, new_bill, prev_title)

                send_message_bills(EDIT_BILLS, history, bills_details)

                generate_debts(group, debts_history)

                return return_edit_bills(new_bill, history)
            else:
                clear_bills(new_bill, bills_details_prev)

                return return_edit_bills(new_bill)

        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def remove_bills(request):
    if request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'bills_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['bills_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        bills_id = request_data['bills_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Bills get
        try:
            bill = Bills.objects.get(id=bills_id, groups_id=groups_id, is_actual=1, is_deleted=0)
        except Bills.DoesNotExist:
            return return_response(FORBIDDEN)

        if not bill.edited_bills_id:
            if bill.users_id.pk != users_id:
                return return_response(FORBIDDEN)
        else:
            if bill.edited_bills_id.users_id.pk != users_id:
                return return_response(FORBIDDEN)

        bill.is_deleted = 1
        bill.save()

        debts_history = {}

        bills_details = BillsDetails.objects.filter(bills_id=bills_id, is_deleted=0)

        for bills_detail in bills_details:
            users_id = bills_detail.users_id.pk

            debts_history.update({users_id: bills_detail.investment_sum - bills_detail.debt_sum})
            bills_detail.is_deleted = 1
            bills_detail.save()

        history = save_history_remove_bills(user, bill)

        group = bill.groups_id
        generate_debts(group, debts_history)

        return return_remove_bills(group, history)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def restore_bills(request):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'bills_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['bills_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        bills_id = request_data['bills_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Bills get
        try:
            bill = Bills.objects.get(id=bills_id, groups_id=groups_id, is_actual=1, is_deleted=1)
        except Bills.DoesNotExist:
            return return_response(FORBIDDEN)

        if not bill.edited_bills_id:
            if bill.users_id.pk != users_id:
                return return_response(FORBIDDEN)
        else:
            if bill.edited_bills_id.users_id.pk != users_id:
                return return_response(FORBIDDEN)

        bill.is_deleted = 0
        bill.save()

        debts_history = {}

        bills_details = BillsDetails.objects.filter(bills_id=bills_id, is_deleted=1)

        for bills_detail in bills_details:
            users_id = bills_detail.users_id.pk

            debts_history.update({users_id: bills_detail.debt_sum - bills_detail.investment_sum})
            bills_detail.is_deleted = 0
            bills_detail.save()

        history = save_history_restore_bills(user, bill)

        group = bill.groups_id
        generate_debts(group, debts_history)

        return return_restore_bills(group, history)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_bills_details(request):
    if request.method == 'GET':
        keys = ['users_id', 'groups_id', 'bills_id']
        for key in keys:
            if key not in request.GET:
                return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
            groups_id = int(request.GET['groups_id'])
            bills_id = int(request.GET['bills_id'])
        except ValueError:
            return return_response(BAD_REQUEST)

        # Members get
        try:
            Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        # Bills get
        try:
            bill = Bills.objects.get(id=bills_id, groups_id=groups_id)
        except Bills.DoesNotExist:
            return return_response(BAD_REQUEST)

        return return_bills_details(bill)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_user_debts(request):
    if request.method == 'GET':

        if 'users_id' not in request.GET:
            return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
        except ValueError:
            return return_response(BAD_REQUEST)

        # Users get
        try:
            user = Users.objects.get(id=users_id)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        return return_user_debts(user)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def add_debts(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        group = member.groups_id

        if group.is_calculated == 1:
            return return_debts(group)

        generate_user_debts(group)

        history = save_history_add_debts(user, group)
        send_message_groups(ADD_DEBTS, history)

        return return_debts(group, history)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def edit_debts(request):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id', 'debts']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['groups_id'], int):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            user = Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        group = member.groups_id

        if group.is_calculated == 0:
            return return_response(BAD_REQUEST)

        debts = request_data['debts']
        history = []
        for debts_key in debts:
            debt = debts[debts_key]

            keys = ['debts_id', 'is_deleted']
            for key in keys:
                if key not in debt:
                    return return_response(BAD_REQUEST)

            if not isinstance(debt['debts_id'], int):
                return return_response(BAD_REQUEST)

            debts_id = debt['debts_id']
            is_deleted = debt['is_deleted']
            try:
                debt = Debts.objects.get(id=debts_id, is_actual=1)
            except Debts.DoesNotExist:
                return return_response(BAD_REQUEST)

            if is_deleted:
                if not debt.is_deleted:
                    debt.is_deleted = 1
                    debt.save()

                    news = save_history_edit_debts(user, debt)
                    send_message_edit_debts(news)
                    history.append(news)

            else:
                if debt.is_deleted:
                    debt.is_deleted = 0
                    debt.save()

                    news = save_history_edit_debts(user, debt)
                    send_message_edit_debts(news)
                    history.append(news)

        return return_edit_debts(group, history)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def get_debts_details(request):
    if request.method == 'GET':
        keys = ['users_id', 'groups_id']
        for key in keys:
            if key not in request.GET:
                return return_response(BAD_REQUEST)

        try:
            users_id = int(request.GET['users_id'])
            groups_id = int(request.GET['groups_id'])
        except ValueError:
            return return_response(BAD_REQUEST)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        return return_debts_details(member)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def remind_about_debts(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'groups_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['groups_id'], int) \
                or not isinstance(request_data['access_token'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        groups_id = request_data['groups_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        # Members get
        try:
            member = Members.objects.get(users_id=users_id, groups_id=groups_id, is_deleted=0)
        except Members.DoesNotExist:
            return return_response(FORBIDDEN)

        if member.groups_id.is_calculated == 0:
            return return_response(BAD_REQUEST)

        send_message_remind_about_debts(member)
        return return_response(OK)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def register_devices(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'reg_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        access_token = request_data['access_token']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        form = RegisterDeviceForm(request_data)

        if form.is_valid():
            save_register_device_form(form)
            return return_response(OK)
        else:
            return return_response(BAD_REQUEST)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def unregister_devices(request):
    if request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return return_response(BAD_REQUEST)

        keys = ['users_id', 'access_token', 'reg_id']
        for key in keys:
            if key not in request_data:
                return return_response(BAD_REQUEST)

        if not isinstance(request_data['users_id'], int) \
                or not isinstance(request_data['access_token'], basestring) \
                or not isinstance(request_data['reg_id'], basestring):
            return return_response(BAD_REQUEST)

        users_id = request_data['users_id']
        access_token = request_data['access_token']
        reg_id = request_data['reg_id']

        if not access_token:
            return return_response(FORBIDDEN)

        # Users get
        try:
            Users.objects.get(id=users_id, access_token=access_token)
        except Users.DoesNotExist:
            return return_response(FORBIDDEN)

        try:
            Device.objects.get(reg_id=reg_id, users_id=users_id).delete()
            return return_response(OK)
        except Device.DoesNotExist:
            return return_response(FORBIDDEN)
    else:
        return return_response(METHOD_NOT_ALLOWED)


def page_not_found(request):
    return return_response(NOT_FOUND)
