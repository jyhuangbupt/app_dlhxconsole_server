# -*- coding: utf-8 -*-
'''控制台用户模块View'''

import sys, traceback, datetime, random
from collections import OrderedDict
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import apphelper, NotAllowed, BadRequest, TooFrequently, SmsCodeError, NotFound
from xdock.apps import XDockBlueprint as Blueprint
from xdock_user.lib.sms import SmsCode
from xdock_user.model import userconfig
from xdock_user import chuanglan_sms
from xdock_user.lib import User, UserRDS, ThirdAccount, ThirdAccountType, UserLevel, UserToken
from xdock_user.lib.usermessage import UserMessage2Template
from xdock_user.lib import User, UserRDS, ThirdAccount, ThirdAccountType, UserLevel
from xdock_user.lib.staff import Staff, StaffRole
# from xdock_dlhx.lib.serviceteam import UserServiceTeam, UserServiceTeamRole, ServiceTeamRoleStatus, UserServiceTeamOwn, UserServiceTeamMember

from . import needlogin
logger = logging.getLogger('Console.faly.User')

blueprint = Blueprint('console.faly.user', __name__, url_prefix='/user')

@blueprint.before_app_request
def before_app_request():
    if request.endpoint and 'static' in request.endpoint:
        return
    if request.endpoint and request.endpoint.split('.')[-1] in ['favicon']:
        return

    # #############通用登录检查代码##############
    # 登录成功后，session中必有phone，单点登录成功用户的身份识别使用phone。
    phone = session.get('phone', None)
    if not phone:
        # 没有登录或者session已经过期
        # session['access_url'] = request.url
        # return redirect('%s://%s/bbsconsole/user/login' % (config.scheme, config.domain))
        return
    # 找到登录的用户
    ta = ThirdAccount(thirdtype=ThirdAccountType.phone, thirdid=phone)
    if not ta.exists:
        raise BadRequest(description='用户不存在！')
    # 如果不为职工，则不允许登录
    staff = Staff(uid=ta.uid)
    if not staff.exists:
        raise BadRequest(description='您不在职工列表内！')
    g.user = User(uid=ta.uid)
    session['user'] = g.user.to_dict()
    session['power'] = []
    urls = []
    staff = Staff(uid=g.user.uid)
    if staff.exists:
        roleids = staff.roleids
        if roleids:
            roles = StaffRole.query(roleid=roleids)
            for r in roles:
                l = r.to_dict().get('permission_urls') if r.to_dict().get('permission_urls') else []
                urls.extend(l)
    session['power'] = '|'.join(list(set(urls)))
    # 拒绝url直接访问
    if str(request.path) in Blueprint.get_allmenu_urls() and str(request.path) not in list(set(urls)):
        raise BadRequest(description='无权限访问！')

class SmsCodeMessage(object):

    __message_id__ = 'user.smscode'

    def __init__(self, phone, smsdata):
        self.phone = phone
        self.smsdata = smsdata

    def send(self):
        template = UserMessage2Template.from_messageid(self.__message_id__)
        if not template or len(template.sms_template) <= 0:
            raise RuntimeError('not configured sms template in db')
        text = template.sms_template % tuple(self.smsdata)
        chuanglan_sms.send_text(self.phone, text)
        logger.info('smscode send', self.phone, text)
        return text

@blueprint.route('/ajax/query/2', methods=['GET', 'POST'])
def api_ajax_query_2():
    '''ajax异步查询用户信息'''
    name = request.values.get('name')
    if name:
        kwargs = {}
        try:
            int(name)
        except:
            kwargs['name'] = name
        else:
            if len(name) == 11:
                kwargs['phone'] = name
            else:
                kwargs['uid'] = name

        users = UserRDS.query(limit=None, offset=None, **kwargs)
    else:
        users = []

    data = {
        'users': [u.to_dict() for u in users]
    }
    return apphelper.format_ok_response(data=data)

@blueprint.route('/index', methods=['GET', 'POST'])
def api_index():
    return render_template('user/index.html')


# @blueprint.route('/query', menu_path='/我/会员/我的直属客户', methods=['GET', 'POST'])
# def api_user_query():
#     page_size = 10
#     uid = request.values.get('target_uid')
#     searchuid = request.values.get('searchuid')
#     form = {
#         'uid': uid,
#         'searchuid': searchuid,
#         'type': 'directly',
#         'next_page': int(request.values.get('next_page') or 1)
#     }
#     if not form.get('uid'):
#         raise BadRequest(description='请求参数错误！')
#     kwargs = {
#         'uid': form.get('uid'),
#         'searchuid': form.get('searchuid'),
#         'type': 'directly',
#         'limit': page_size,
#         'offset': (form.get('next_page')-1)*page_size
#     }
#     users, total_count = UserServiceTeam.query_customers(**kwargs)
#     if users:
#         users = [u.to_dict(extra_keys=['level']) for u in users]
#     else:
#         users = []
#     # 查询总数
#     # total_count = MyCustomer.query_customers(count=True, **kwargs)
#     total_pages = (total_count + page_size - 1) / page_size
#     levels = UserLevel.queryall_ordereddict()
#     return render_template('user/user_query.html', form=form, users=users if users else [], levels=levels, page=form.get('next_page'), total_count=total_count, total_pages=total_pages)



@blueprint.route('/smscode/send/ajax', methods=['GET', 'POST'])
def api_user_login_smscode_send_ajax():
    phone = request.values.get('phone')
    if not phone or len(phone) != 11:
        return apphelper.format_response(meta={'code': 400, 'message': BadRequest.__name__, 'description': u'请输入正确的11位手机号！'})
    seconds = 300
    # 先保存生成的验证码
    sc = SmsCode(phone=phone)
    # 检查频率
    if not sc.is_allowed(seconds):
        raise TooFrequently(description=u'验证码发送太频繁，请稍后再试！')
    smscode = str(random.randint(1000,9999))
    sc.save_smscode(smscode, seconds)
    # 不在白名单的话，发送验证码
    if phone not in userconfig.whitelist:
        SmsCodeMessage(phone, (smscode, '手机认证', seconds/60)).send()
    else:
        logger.debug('smscode send ignored whitelist phone %s.' % phone)

    return apphelper.format_ok_response(data={})


@blueprint.route('/login/token/get/ajax', methods=['GET', 'POST'])
def api_user_login_token_get_ajax():
    '''获取用于登录的验证码'''
    phone = request.values.get('phone')
    smscode = request.values.get('smscode')
    if not all([phone, len(phone)==11, smscode]):
        return apphelper.format_response(meta={'code': 400, 'message': BadRequest.__name__, 'description': u'请输入正确的手机号和验证码！'})

    # 验证码检验
    sc = SmsCode(phone=phone)
    if phone not in userconfig.whitelist and not sc.verify_smscode(smscode, seconds=300):
        return apphelper.format_response(meta={'code': 400, 'message': SmsCodeError.__name__, 'description': u'请输入正确的验证码！'})

    ta = ThirdAccount(thirdtype=ThirdAccountType.phone, thirdid=phone)
    if not ta.exists or ta.uid is None:
        return apphelper.format_response(meta={'code': 400, 'message': NotFound.__name__, 'description': u'该账号不存在！'})

    usertoken = UserToken(uid=ta.uid, appid=config.appids[0])
    return apphelper.format_ok_response(data={'token': usertoken.token})


@blueprint.route('/login', methods=['GET', 'POST'])
def api_user_login():
    if request.method != 'POST':
        # 进入登录界面
        return render_template('user/login.html', _from=request.values.get('_from')or'login')
    else:
        # 验证表单
        phone = request.form.get('phone')
        token = request.form.get('token')
        if not all([phone, token]):
            return render_template('user/login.html', message={'alert': '输入错误，请重新登录！'})
        ta = ThirdAccount(thirdtype=ThirdAccountType.phone, thirdid=phone)
        if not ta.exists:
            return render_template('user/login.html', message={'alert': '该账户不存在，请先注册HNK帐号，并绑定手机号.'})
        usertoken = UserToken(uid=ta.uid, appid=config.appids[0])
        if usertoken.token != token:
            return render_template('user/login.html', message={'alert': '输入错误，请重新登录！'})

        # 巴迪家族平台所有运营环境以手机号作为session单点登录连接信息
        session['phone'] = phone

        access_url = session.pop('access_url', None)
        if access_url:
            return redirect(access_url)
        return redirect('/%s/platform/index' % config.appname)


@blueprint.route('/logout', methods=['GET'])
def api_user_logout():
    favorite_url = session.get('_favorite_url', None)
    session.pop('phone', None)
    session.clear()
    session['_favorite_url'] = favorite_url
    return redirect('/%s/user/login?_from=logout' % (config.appname))


