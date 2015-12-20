#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from time import strftime


ADD_GROUPS = 0
EDIT_GROUPS = 1
ADD_MEMBERS = 2
REMOVE_MEMBERS = 3
ADD_BILLS = 4
EDIT_BILLS = 5
REMOVE_BILLS = 6
ADD_DEBTS = 7
EDIT_DEBTS = 8
RESTORE_BILLS = 9
REMIND_ABOUT_DEBTS = 10
HISTORY_ACTION_CHOICES = (
    (ADD_GROUPS, 'создал группу'),
    (EDIT_GROUPS, 'изменил название группы на'),
    (ADD_MEMBERS, 'пригласил'),
    (REMOVE_MEMBERS, 'исключил'),
    (ADD_BILLS, 'добавил счет'),
    (EDIT_BILLS, 'отредактировал счет'),
    (REMOVE_BILLS, 'удалил счет'),
    (ADD_DEBTS, 'рассчитал группу'),
    (EDIT_DEBTS, 'отдал долг'),
    (RESTORE_BILLS, 'восстановил счет')
)

SAY = 'сказал'
WHAT = ', что'

MAN = 0
WOMAN = 1
SEX_CHOICES = (
    (MAN, 'Мужчина'),
    (WOMAN, 'Женщина'),

)


class UnixTimestampField(models.DateTimeField):
    """UnixTimestampField: creates a DateTimeField that is represented on the
    database as a TIMESTAMP field rather than the usual DATETIME field.
    """
    def __init__(self, null=False, blank=False, **kwargs):
        super(UnixTimestampField, self).__init__(**kwargs)
        # default for TIMESTAMP is NOT NULL unlike most fields, so we have to
        # cheat a little:
        self.blank, self.isnull = blank, null
        self.null = True  # To prevent the framework from shoving in "not null".

    def db_type(self, connection):
        typ = ['TIMESTAMP']
        # See above!
        if self.isnull:
            typ += ['NULL']
        if self.auto_created:
            typ += ['default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP']
        return ' '.join(typ)

    def to_python(self, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        else:
            return models.DateTimeField.to_python(self, value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        # Use '%Y%m%d%H%M%S' for MySQL < 4.1
        return strftime('%Y-%m-%d %H:%M:%S', value.timetuple())


class Users(models.Model):
    vk_id = models.BigIntegerField(null=True)
    last_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    sex = models.BooleanField(choices=SEX_CHOICES, default=MAN)
    access_token = models.TextField(default="")
    is_deleted = models.BooleanField(default=0)


class Friends(models.Model):
    users_id = models.ForeignKey(Users, related_name='Friends_id')
    users_id_added = models.ForeignKey(Users, related_name='Friends_id_added')
    is_deleted = models.BooleanField(default=0)


class Groups(models.Model):
    users_id = models.ForeignKey(Users)
    title = models.CharField(max_length=100)
    creation_datetime = UnixTimestampField(auto_created=True)
    update_datetime = UnixTimestampField(auto_created=True)
    is_calculated = models.BooleanField(default=0)
    is_deleted = models.BooleanField(default=0)


class Members(models.Model):
    users_id = models.ForeignKey(Users)
    groups_id = models.ForeignKey(Groups)
    is_deleted = models.BooleanField(default=0)


class Bills(models.Model):
    users_id = models.ForeignKey(Users)
    groups_id = models.ForeignKey(Groups)
    title = models.CharField(max_length=100)
    sum = models.IntegerField(default=0)
    creation_datetime = UnixTimestampField(auto_created=True)
    # последний
    is_actual = models.BooleanField(default=0)
    edited_bills_id = models.ForeignKey("self", null=True)
    # удален
    is_deleted = models.BooleanField(default=0)


class BillsDetails(models.Model):
    groups_id = models.ForeignKey(Groups)
    bills_id = models.ForeignKey(Bills)
    users_id = models.ForeignKey(Users)
    debt_sum = models.IntegerField(default=0)
    investment_sum = models.IntegerField(default=0)
    # погашен = не нужно брать для детализации долгов
    is_actual = models.BooleanField(default=1)
    # удален
    is_deleted = models.BooleanField(default=0)
    creation_datetime = UnixTimestampField(auto_created=True)


class Debts(models.Model):
    users_id_who = models.ForeignKey(Users, related_name='Debts_id_who', null=True)
    users_id_whom = models.ForeignKey(Users, related_name='Debts_id_whom', null=True)
    groups_id = models.ForeignKey(Groups)
    sum = models.IntegerField()
    # пересчитан
    is_actual = models.BooleanField(default=1)
    # погашен
    is_deleted = models.BooleanField(default=0)


class History(models.Model):
    users_id_who_say = models.ForeignKey(Users, related_name='History_id_who_say', null=True)
    users_id_who = models.ForeignKey(Users, related_name='History_id_who')
    users_id_whom = models.ForeignKey(Users, related_name='History_id_whom', null=True)
    groups_id = models.ForeignKey(Groups)
    bills_id = models.ForeignKey(Bills, null=True)
    debts_id = models.ForeignKey(Debts, null=True)
    action = models.IntegerField(choices=HISTORY_ACTION_CHOICES, default=ADD_GROUPS)
    action_datetime = UnixTimestampField(auto_created=True)
    text_who_say = models.CharField(max_length=100, null=True)
    text_say = models.CharField(max_length=15, null=True)
    text_who = models.CharField(max_length=100)
    text_description = models.CharField(max_length=100)
    text_what_whom = models.CharField(max_length=102)

