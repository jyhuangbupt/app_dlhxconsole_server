# -*- coding: utf-8 -*-
'''控制台activityView'''
import time

import sys, traceback, datetime, random
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import apphelper, NotAllowed, BadRequest, TooFrequently, SmsCodeError, NotFound
from xdock.apps import XDockBlueprint as Blueprint
from xdock_user.lib import User, UserRDS, UserLevel, UserLevelStatus
from xdock_jiamei.lib.activity import *
from . import needlogin
logger = logging.getLogger('Console.jiamei.activity')

blueprint = Blueprint('console.jiamei.activity', __name__, url_prefix='/activity')

@blueprint.route('', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
def api_index():
    return render_template('activity/index.html')



@blueprint.route('/query', menu_path='平台运营/活动管理/活动列表', methods=['GET', 'POST'])
@needlogin
def api_jiamei_activity():
    '''活动列表'''
    page_size = 20
    form = {
        'name': request.values.get('name'),
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size,
        'startdate': request.values.get('startdate'),
        'enddate': request.values.get('enddate'),
        'status': request.values.get('status') or "",
    }
    kwargs = {
        'name': form.get('name'),
        'limit': page_size,
        'offset': (form['next_page'] - 1) * page_size,
        'startdate': form.get('startdate'),
        'enddate': form.get('enddate'),
        'status': form.get('status')
    }
    activitylist = Activity.query(**kwargs)
    activitys = []
    for activity in activitylist:
        users = ActivityUser.query(activityid=activity.activityid, status='normal')
        count = 0
        for user in users:
            count = count + int(user.count)
        activity = activity.to_dict()
        activity['enroll_count'] = count
        activitys.append(activity)
    # 查询总数
    total_count = Activity.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size

    return render_template('activity/activity_list.html', ActivityStatus=ActivityStatus, form=form, activitys=activitys,
                           page=form['next_page'], total_pages=total_pages, total_count=total_count)


@blueprint.route('/offset/ajax', methods=['GET', 'POST'])
@needlogin
def api_jiamei_activity_offset_ajax():
    '''活动下架'''
    activity = Activity(activityid=request.values.get('activityid'))
    if not activity.exists:
        raise BadRequest(description='该内容不存在！')
    if activity.status == ActivityStatus.published:
        activity.status = ActivityStatus.editing
        activity.save()
    return apphelper.format_ok_response()

@blueprint.route('/publish/ajax', methods=['GET', 'POST'])
@needlogin
def api_jiamei_activity_publish_ajax():
    '''游学产品上架'''
    activity = Activity(activityid=request.values.get('activityid'))
    if not activity.exists:
        raise BadRequest(description='该内容不存在！')
    if activity.status == ActivityStatus.editing:
        activity.status = ActivityStatus.published
        activity.save()
    return apphelper.format_ok_response()


@blueprint.route('/stick/ajax', methods=['POST'])
@needlogin
def api_jiamei_activity_stick_ajax():
    activity = Activity(activityid=request.values.get('activityid'))
    if not activity.exists:
        raise BadRequest(description='该内容不存在！')

    activity.ot = int(time.time()*1000)
    activity.save()
    return apphelper.format_ok_response()


@blueprint.route('/delete/ajax', methods=['POST'])
@needlogin
def api_jiamei_activity_delete_ajax():
    activityid = request.values.get('activityid')
    activity = Activity(activityid=activityid)
    if activity.exists:
        activity.delete()
    return apphelper.format_ok_response()

@blueprint.route('/update', menu_path='平台运营/活动管理/活动创建', methods=['GET', 'POST'])
@needlogin
def api_jiamei_activity_update():
    if request.method == 'GET':
        activityid = request.values.get('activityid')
        if activityid:
            activity = Activity(activityid=activityid)
            activity = activity.to_dict()
        else:
            activity = {'start_time_ui': '', 'end_enroll_time_ui': ''}
        return render_template('activity/activity_update.html', activity=activity)
    else:
        activityid = request.values.get('activityid')
        if not activityid:
            activity = Activity(activityid=utils.uuid1())
            activity.ot = int(time.time() * 1000)
            activity.remain_count = request.values.get('max_count') or 0
            activity.status = ActivityStatus.editing
        else:
            activity = Activity(activityid=activityid)
            # 查询此活动下已报名人数
            users = ActivityUser.query(activityid=activityid, status="normal")
            count = 0
            for user in users:
                count = count + int(user.count)
            new_remain = int(request.values.get('max_count')) - count
            activity.remain_count = new_remain if new_remain>0 else 0
        activity.name = request.values.get('name') or ""
        activity.start_time = request.values.get('start_time') or ""
        activity.end_enroll_time = request.values.get('end_enroll_time') or ""
        activity.invitation = request.values.get('invitation') or ""
        activity.max_count = request.values.get('max_count') or 0
        activity.every_count = request.values.get('every_count') or 0
        activity.save()
        return apphelper.format_ok_response()

@blueprint.route('/user/query', methods=['GET', 'POST'])
def api_jiamei_activity_user_query():
    activityid = request.values.get('activityid')
    if not activityid:
        raise BadRequest(description='活动id不能为空！')
    users = ActivityUser.query(activityid=activityid)
    newusers = []
    for user in users:
        temp_user = UserRDS(uid=user.uid)
        if not temp_user.phone:
            temp_user = {'info': {}}
        user = user.to_dict()
        user['user'] = temp_user

        newusers.append(user)
    return render_template('activity/activity_user.html', users=newusers)


@blueprint.route('/blacklist/add', methods=['POST'])
@needlogin
def api_jiamei_activity_blacklist_add():
    phone = request.values.get('phone')
    user = UserRDS.query(phone=phone)
    if len(user) == 0:
        raise BadRequest(description='该会员不存在！')
    blacklist = ActivityBlacklist(uid=user[0].uid)
    blacklist.save()
    return redirect('/%s/activity/blacklist/query' % (config.appname))


@blueprint.route('/blacklist/query', methods=['POST','GET'])
@needlogin
def api_jiamei_activity_blacklist_query():
    page_size = 20
    form = {
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size,
    }
    kwargs = {
        'limit': page_size,
        'offset': (form['next_page'] - 1) * page_size,
    }
    blacklists = ActivityBlacklist.query(**kwargs)
    users = []
    for blacklist in blacklists:
        user = UserRDS(uid=blacklist.uid)
        users.append(user.to_dict())
    # 查询总数
    total_count = ActivityBlacklist.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size

    return render_template('activity/activity_blacklist.html', users=users,
                           page=form['next_page'], total_pages=total_pages, total_count=total_count)

@blueprint.route('/blacklist/delete', methods=['POST'])
@needlogin
def api_jiamei_activity_blacklist_delete():
    uid = request.values.get('uid')
    blacklist = ActivityBlacklist(uid=uid)
    if blacklist.exists:
        blacklist.delete()
    return apphelper.format_ok_response()
