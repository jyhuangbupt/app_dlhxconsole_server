# -*- coding: utf-8 -*-
'''控制台FIBI模块View'''

import sys, traceback, datetime
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import NotAllowed, NotFound, BadRequest
from xdock.yunqq.qiyehao import qiyehao_message
from xdock_user.lib import User
from xdock_user.lib.usermessage import UserMessage2, UserMessage2History, UserMessage2Category, UserMessage2Template
from xdock_user.model import userconfig


logger = logging.getLogger('Console.Utils.View')


blueprint = Blueprint('console.utils', __name__, url_prefix='/utils')


@blueprint.route('/sms/send', methods=['GET','POST'])
def api_utils_sms_send():
    # 获取登录入口
    entry = request.values.get('entry')
    target_uid = request.values.get('target_uid')
    target_user = User(uid=target_uid)
    # 短信模板不再从配置文件读取 旧设计 key: 配置文件短信编号 value: 短信模板
    # 使用数据库内用户消息模板 key: templateid value: sms_template
    templates = [t.to_dict() for t in UserMessage2Template.query(isconsolesms='true') if t.sms_template]
    templates.sort(key=lambda t: t.get('name'))
    smses = UserMessage2History.query(uid=target_user.uid, category=UserMessage2Category.sms, limit=30, offset=0)
    smses = [s.to_dict() for s in smses]

    if request.method == 'GET':
        return render_template('%s/sms_send.html' % ('user' if entry=='mine' else 'utils'), target_user=target_user.to_dict(), templates=templates, smses=smses, msg=request.values.get('msg') or '')
    else:
        if not target_user.phone:
            return redirect('/%s/sms/send?entry=%s&target_uid=%s&msg=%s' % (config.appname, entry or '', target_uid, '用户手机号不存在！'))
        templateid = request.values.get('templateid')
        if not templateid:
            return redirect('/%s/sms/send?entry=%s&target_uid=%s&msg=%s' % (config.appname, entry or '', target_uid, '请选择模板'))
        t = UserMessage2Template(templateid=templateid)
        argslength = len(t.sms_template.split('%s')) - 1
        args = []
        for i in range(argslength):
            arg = request.values.get('arg%s' % i)
            if arg:
                args.append(arg)
        if len(args) != argslength:
            return redirect('/%s/sms/send?entry=%s&target_uid=%s&msg=%s' % (config.appname, entry or '', target_uid, '参数个数不一致！'))
        rs = UserMessage2.send_sms(target_user.uid, target_user, templateid, *args )
        qiyehao_message.send_text('【用户管理】\n\n短信发送成功！\n\n用户：%s\n手机号：%s\n内容：%s' % (target_user.name or target_user.nickname, target_user.phone, rs))
        # return render_template('%s/sms_send.html' % ('user' if entry=='mine' else 'utils'), target_user=target_user.to_dict(), templates=templates, smses=smses, msg='发送成功！' if rs else '发送失败！')
        return redirect('/%s/utils/sms/send?entry=%s&target_uid=%s&msg=%s' % (config.appname, entry or '', target_uid, '发送成功' if rs else '发送失败'))
