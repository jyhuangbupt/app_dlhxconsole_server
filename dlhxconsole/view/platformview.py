# -*- coding: utf-8 -*-
import sys, traceback, datetime, time, copy,re,xlrd
import flask_excel as excel #下载excel
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from collections import OrderedDict
from . import needlogin
from xdock.bases import json, utils, config, logging
from xdock.apps import NotAllowed, NotFound, BadRequest, apphelper
from xdock.apps import XDockBlueprint as Blueprint
from xdock.models.libmodels import RDSLibModel
from xdock.yunqq.qiyehao import qiyehao_message
from xdock_user.lib import User, UserRDS, UserLevel, UserLevelStatus
from xdock_user.lib import User, ThirdAccount, ThirdAccountType
from xdock_user.lib.staff import StaffRoleStatus, StaffRole, StaffPostStatus, StaffPost, Staff
from xdock_user.lib import userconfig
from xdock_crm.lib.marketrecord import CRMMarketRecord
from xdock_user.lib.user import __usersignal__

logger = logging.getLogger('console.dlhx.platform.view')

blueprint = Blueprint('console.dlhx.platform', __name__, url_prefix='/platform')

@blueprint.route('', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
def api_index():
    return render_template('platform/index.html')


# 报名名单查询
@blueprint.route('/enroll/list/query', methods=['GET', 'POST'])
@needlogin
def api_platform_vip_card_query():
    page_size = 20
    form = {
        'status': request.values.get('status'),
        'next_page': int(request.values.get('next_page') or 1)
    }
    kwargs = {
        'status': request.values.get('status'),
        'limit': page_size,
        'offset': (form.get('next_page') - 1) * page_size
    }
    vipcards = VipCard.query(**kwargs)
    cards = []
    for v in vipcards:
        product = Product(productid=v.productid)
        count_user = JiameiVip.query(cardid=v.cardid, count=True)
        count_remain = JiameiVip.query(cardid=v.cardid, count=True, hasremain=True)
        v.product = product
        v.count_user = count_user
        v.count_remain = count_remain
        cards.append(v)
    # 查询总数
    total_count = VipCard.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('platform/vip_card_query.html', form=form, cards=cards, statuses=dict(VipCardStatus), page=form.get('next_page'), total_count=total_count, total_pages=total_pages)

@blueprint.route('/user/query', menu_path='平台运营/会员/会员管理', methods=['GET', 'POST'])
@needlogin
def api_platform_user_query():
    page_size = 20
    form = {
        'name': request.values.get('name'),
        'is_subscribe': request.values.get('is_subscribe'),
        'is_deleted': request.values.get('is_deleted'),
        'next_page': int(request.values.get('next_page') or 1),
        'is_subscribe_miniapp': request.values.get('is_subscribe_miniapp')
    }

    kwargs = {
        'is_subscribe': form.get('is_subscribe'),
        'is_deleted': request.values.get('is_deleted'),
        'limit': page_size,
        'offset': (form.get('next_page')-1)*page_size,
        'is_subscribe_miniapp': request.values.get('is_subscribe_miniapp')
    }
    if form.get('name'):
        try:
            int(form.get('name'))
        except:
            kwargs['name'] = form.get('name')
        else:
            if len(form.get('name')) == 11:
                kwargs['phone'] = form.get('name')
            else:
                kwargs['uid'] = form.get('name')
    users = UserRDS.query(**kwargs)
    newusers = []
    for u in users:
        jiameiVip = JiameiVip.query(uid=u.uid)
        vips = []
        for j in jiameiVip:
            vipcard = VipCard(cardid=j.cardid)
            vipcard.num = j.remain
            vips.append(vipcard)
        u = u.to_dict()
        u['vips'] = [vip.to_dict() for vip in vips]
        newusers.append(u)
    users = newusers
    # 查询总数
    total_count = UserRDS.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    if request.values.get('type') == "ajax":
        # 兼容非跳转页面查询
        return apphelper.format_ok_response(data=users)
    else:
        return render_template('platform/user_query.html', form=form, users=users,  page=form.get('next_page'), total_count=total_count, total_pages=total_pages)

@blueprint.route('/user/setdelete', methods=['GET', 'POST'])
@needlogin
def api_platform_user_setdelete():
    user = UserRDS.query(uid=request.values.get('uid'))
    if len(user)<1:
        raise BadRequest(description='用户不存在！')
    deleted = request.values.get('deleted')
    user[0].is_deleted = deleted
    user[0].save()
    return apphelper.format_ok_response()

@blueprint.route('/user/detail', methods=['GET', 'POST'])
@needlogin
def api_platform_user_detail():
    # 获取登录入口
    entry = request.values.get('entry')
    target_user = UserRDS(uid=request.values.get('target_uid'))
    jiameiVip = JiameiVip.query(uid=target_user.uid)
    vips = []
    for j in jiameiVip:
        vipcard = VipCard(cardid=j.cardid)
        vipcard.num = j.remain
        vips.append(vipcard)


    newtarget_user = target_user.to_dict()
    newtarget_user['vips'] = vips
    preorders = PreOrder.query(uid=target_user.uid)
    if len(preorders) > 0:
        haspreorder = True
        preorder = preorders[0].to_dict()
    else:
        preorder = {}
        haspreorder = False
    newtarget_user['preorder'] = preorder
    newtarget_user['haspreorder'] = haspreorder
    marketrecords = CRMMarketRecord.query(uid=request.values.get('target_uid'))
    marketrecords = [cr.to_dict() for cr in marketrecords]
    return render_template('%s/user_detail.html' % ('user' if entry=='mine' else 'platform'),
        user=newtarget_user,
        isstaff=True if Staff(uid=target_user.uid).exists else False,
        levels={l.levelid: l.to_dict() for l in UserLevel.query()},
        third_accounts=target_user.third_accounts, userconfig=userconfig, ThirdAccountType=ThirdAccountType, marketrecords=marketrecords)

@blueprint.route('/user/ajax/thirdaccount/unbind', methods=['GET', 'POST'])
@needlogin
def api_ajax_thirdaccount_unbind():
    '''ajax异步查询用户信息'''
    thirdtype = request.values.get('thirdtype')
    target_uid = request.values.get('target_uid')
    user = User(uid=target_uid)
    thirdid = user.third_accounts.get(thirdtype)
    td = ThirdAccount(thirdtype=thirdtype, thirdid=thirdid)
    thirdinfo = td.thirdinfo
    user.unbind(thirdtype)
    userRds = UserRDS(uid=target_uid)
    userRds.is_subscribe_miniapp = 'false'
    userRds.save()
    return apphelper.format_ok_response()

@blueprint.route('/user/upload', methods=['GET', 'POST'])
@needlogin
def api_platform_user_upload():
    if request.method == 'POST':
        file = request.files['file']
        f = file.read()
        data = xlrd.open_workbook(file_contents=f)
        table = data.sheets()[0]
        names = data.sheet_names()  # 返回book中所有工作表的名字
        status = data.sheet_loaded(names[0])  # 检查sheet1是否导入完毕
        nrows = table.nrows  # 获取该sheet中的有效行数
        # ncols = table.ncols  # 获取该sheet中的有效列数
        phone_update_line = ''
        phone_error_line = ''
        for index in range(1, nrows, 1):
            # ["姓名", "手机号", "会员编号及份数"]
            u = table.row_values(index)  # 第i行数据
            # 检查手机号合法性
            try:
                phone = str(int(u[1]))
            except:
                phone_error_line = phone_error_line + str(index) + ','
                continue
            ret = re.match(r'^1[356789][0-9]{9}$', phone)
            if not ret:
                phone_error_line = phone_error_line + str(index)+','
                continue
            ta = ThirdAccount(thirdtype=ThirdAccountType.phone, thirdid=phone)
            # 判断用户是否存在
            if ta.exists:
                #用户已存在，更改会员信息
                user = UserRDS.query(phone=ta.thirdid)
                user[0].name = u[0]
                user[0].save()
                # 更新会员 会员格式VIP1-12|VIP2-12
                vips = u[2].split('|')
                phone_update_line = phone_update_line + str(index) + ','
                for v in vips:
                    card_num = v.split('-')[0]
                    remain = v.split('-')[1]
                    card = VipCard.query(card_num=card_num)
                    if len(card) < 1:
                        continue
                    vip = JiameiVip.query(uid=user[0].uid, cardid=card[0].cardid)
                    if len(vip) < 1:
                        #之前未创建会员
                        vip = JiameiVip(vipid=utils.uuid1())
                    else:
                        vip = vip[0]
                    vip.cardid = card[0].cardid
                    vip.uid = user[0].uid
                    vip.remain = remain
                    vip.save()
            #  创建会员并开通相关会员权益
            # 注册用户
            else:
                user = User.signup(config.appids[0], 'console', ThirdAccountType.phone, ta.thirdid)
                user.name = u[0]
                user.save()
                # 开通会员 会员格式VIP1-12|VIP2-12
                vips = u[2].split('|')
                for v in vips:
                    card_num = v.split('-')[0]
                    remain = v.split('-')[1]
                    card = VipCard.query(card_num=card_num)
                    if len(card) < 1:
                        continue
                    vip = JiameiVip(vipid=utils.uuid1())
                    vip.cardid = card[0].cardid
                    vip.uid = user.uid
                    vip.remain = remain
                    vip.save()
        return render_template('platform/user_upload.html', message='会员创建成功', phone_update_line=phone_update_line, phone_error_line=phone_error_line)
    return render_template('platform/user_upload.html')

@blueprint.route('/user/download', methods=['GET', 'POST'])
@needlogin
def api_platform_user_download():
    page_size = 1000
    form = {
        'name': request.values.get('name'),
        'is_subscribe_miniapp': request.values.get('is_subscribe_miniapp'),
        'is_deleted': request.values.get('is_deleted'),
        'next_page': int(request.values.get('next_page') or 1)
    }

    kwargs = {
        'is_subscribe_miniapp': form.get('is_subscribe_miniapp'),
        'is_deleted': request.values.get('is_deleted'),
        'limit': page_size,
        'offset': (form.get('next_page') - 1) * page_size,
        'name': form.get('name')
    }
    if form.get('name'):
        try:
            int(form.get('name'))
        except:
            kwargs['name'] = form.get('name')
        else:
            if len(form.get('name')) == 11:
                kwargs['phone'] = form.get('name')
            else:
                kwargs['uid'] = form.get('name')
    users = UserRDS.query(**kwargs)
    exports = [[
        '姓名',
        '手机号',
        '会员类型及份数',
        '小程序注册',
        '会员名称及份数',
        '会员是否有效'
    ]]
    if len(users) > 0:
        for user in users:
            name = user.name
            phone = user.phone
            uid = user.uid
            vips = JiameiVip.query(uid=uid)
            vipStr = ''
            vipChinese = ''
            for index in range(0, len(vips),1):
                card = VipCard(cardid=vips[index].cardid)
                if index != (len(vips)-1):
                    vipStr = vipStr + card.card_num+'-'+str(vips[index].remain)+'|'
                    vipChinese = vipChinese +card.name+'*'+str(vips[index].remain)+'；'
                else:
                    vipStr = vipStr + card.card_num + '-' + str(vips[index].remain)
                    vipChinese = vipChinese + card.name + '*' + str(vips[index].remain) + '；'
            try:
                if 'weixinminiapp' in user.third_accounts.keys():
                    is_subscribe_miniapp = "是"
                else:
                    is_subscribe_miniapp = "否"
            except:
                is_subscribe_miniapp = "否"
            if user.is_deleted == 'true':
                is_deleted = "无效会员"
            else:
                is_deleted = "有效会员"
            u = [
                name,
                phone,
                vipStr,
                is_subscribe_miniapp,
                vipChinese,
                is_deleted
            ]
            exports.append(u)
    return excel.make_response_from_array(exports, "xlsx", file_name="users")


@blueprint.route('/user/create', methods=['GET', 'POST'])
@needlogin
def api_platform_user_create():
    levels = UserLevel.queryall_ordereddict()
    if request.method == 'GET':
        return render_template('platform/user_create.html', levels=levels, form={})
    else:
        form = {
            'name': request.values.get('name'),
            'phone': request.values.get('phone'),
            'note': request.values.get('note'),
        }
        try:
            # 检查手机号合法性
            int(form.get('phone'))
            if len(form.get('phone')) != 11 or int(form.get('phone')[0]) != 1:
                raise RuntimeError('手机号不合法')
        except:
            return render_template('platform/user_create.html', form=form, msg='手机号格式不正确，手机号格式需为11位数字！')
        # 检查是否存在
        ta = ThirdAccount(thirdtype=ThirdAccountType.phone, thirdid=form.get('phone'))
        if ta.exists:
            return render_template('platform/user_create.html', form=form, levels=levels, msg='该手机号已经有会员在使用！')
        # 注册用户
        user = User.signup(config.appids[0], 'console', ThirdAccountType.phone, ta.thirdid)
        user.name = form.get('name')
        user.note = form.get('note')
        user.save()
        return render_template('platform/user_create.html', form=form, msg='会员创建成功')

@blueprint.route('/user/custom/create', methods=['GET', 'POST'])
@needlogin
def api_platform_user_custom_create():
    if request.method == 'GET':
        return render_template('platform/user_custom_create.html', form={})
    else:
        form = {
            'userid': request.values.get('userid'),
            'name': request.values.get('name'),
            'avatar': request.values.get('avatar')
        }
        bool_userid = re.match(r"^[a-zA-Z0-9]*[a-zA-Z0-9]*$", form.get('userid')) and True or False
        # 检查是否只是数字与字母组合
        if not bool_userid:
            return render_template('platform/user_custom_create.html', form=form, msg='自定义账号只能是数字与字母组合！')
        # 检查是否存在
        ta = ThirdAccount(thirdtype=ThirdAccountType.userid, thirdid=form.get('userid'))
        if ta.exists:
            return render_template('platform/user_custom_create.html', form=form, msg='该账号已经有用户在使用！')
        # # 注册用户
        user = User.signup(config.appids[0], 'console', ThirdAccountType.userid, ta.thirdid)
        user.name = form.get('name')
        user.avatar = form.get('avatar')
        user.save()
        # qiyehao_message.send_text('【用户管理】\n\n运营平台自定义用户创建成功！\n\n账号：%s\n姓名：%s\n用户ID：%s\n' % (ta.thirdid, user.name, user.uid))
        return redirect('/%s/platform/user/update?target_uid=%s&msg=%s' % (config.appname, user.uid, u'创建成功!'))


@blueprint.route('/user/update', methods=['GET', 'POST'])
@needlogin
def api_platform_user_update():
    # 获取登录入口
    entry = request.values.get('entry')
    uid = request.values.get('target_uid')
    target_user = User(uid=uid)
    if not target_user.exists:
        raise BadRequest(description='用户不存在！')
    if request.method == 'GET':
        return render_template('%s/user_update.html' % ('user' if entry=='mine' else 'platform'), form={}, user=target_user.to_dict(), third_accounts=target_user.third_accounts_detail, msg=request.values.get('msg') or '')
    else:
        form = {
            'name': request.values.get('name'),
            'phone': request.values.get('phone'),
            'weixinid': request.values.get('weixinid'),
            'inviteruid': request.values.get('inviter_uid'),
            'levelid': request.values.get('levelid'),
            'note': request.values.get('note'),
            'birthday': request.values.get('birthday')
        }

        # 先处理子账户删除和绑定逻辑
        for thirdtype in ThirdAccountType:
            thirdid = target_user.third_accounts.get(thirdtype)
            if thirdtype not in form or thirdid == form.get(thirdtype):
                # 没变
                continue

            # 处理变了的逻辑
            thirdid = form.get(thirdtype)
            if not thirdid and userconfig.signup_account_type == thirdtype:
                return render_template('%s/user_update.html' % ('user' if entry=='mine' else 'platform'), form=form, user=target_user.to_dict(), levels=levels, third_accounts=target_user.third_accounts_detail, msg='主账户不允许被删除！可以修改，不能删除！')
            if not thirdid:
                # 删除该子账户
                target_user.unbind(thirdtype)
                # qiyehao_message.send_text('【用户管理】\n\n删除%s%s成功！\n\n手机：%s\n姓名：%s\n昵称：%s\n级别：%s\n用户ID：%s\n微信号：%s' % (ThirdAccountType.name(thirdtype), thirdid, target_user.phone, target_user.name, target_user.nickname, target_user.level.get('name') or '', target_user.uid, target_user.weixinid))
            else:
                # 修改该子账户
                # 检查手机号合法性
                if thirdtype == ThirdAccountType.phone:
                    try:
                        int(thirdid)
                        if len(thirdid) != 11 or int(thirdid[0]) != 1:
                            raise RuntimeError('手机号不合法')
                    except:
                        return render_template('%s/user_update.html' % ('user' if entry=='mine' else 'platform'), form=form, user=target_user.to_dict(), levels=levels, third_accounts=target_user.third_accounts_detail, msg='手机号格式不正确，手机号格式需为11位数字！')

                # 检查是否存在
                ta = ThirdAccount(thirdtype=thirdtype, thirdid=thirdid)
                if ta.exists:
                    return render_template('%s/user_update.html' % ('user' if entry=='mine' else 'platform'), form=form, user=target_user.to_dict(), third_accounts=target_user.third_accounts_detail, msg='指定%s已经有用户在使用，请更换！' % ThirdAccountType.name(thirdtype))
                target_user.unbind(thirdtype)
                target_user.bind(thirdtype, thirdid)
                # qiyehao_message.send_text('【用户管理】\n\n绑定%s%s成功！\n\n手机：%s\n姓名：%s\n昵称：%s\n级别：%s\n用户ID：%s\n微信号：%s' % (ThirdAccountType.name(thirdtype), thirdid,  target_user.phone, target_user.name, target_user.nickname, target_user.level.get('name') or '', target_user.uid, target_user.weixinid))

        # 基本信息修改
        target_user.name = form.get('name')
        target_user.weixinid = form.get('weixinid')
        target_user.note = form.get('note')
        oldlevelid = target_user.levelid
        target_user.levelid = form.get('levelid')
        target_user.birthday = form.get('birthday')
        target_user.save()
        # qiyehao_message.send_text('【用户管理】\n\n修改成功！\n\n手机：%s\n姓名：%s\n昵称：%s\n级别：%s\n用户ID：%s\n微信号：%s\n邀请人：%s' % (target_user.phone, target_user.name, target_user.nickname, target_user.level.get('name') or '', target_user.uid, target_user.weixinid, (inviter.name or inviter.nickname)))
        if oldlevelid != form.get('levelid'):
            __usersignal__.send(__usersignal__.levelupdate, target_user)
        return redirect('/%s/platform/user/update?entry=%s&target_uid=%s&msg=%s' % (config.appname, entry or '', target_user.uid, u'保存成功!'))

@blueprint.route('/staff/role/query', menu_path='平台运营/员工管理/角色管理（权限控制）', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_role_query():
    page_size = 10
    form = {
        'status': request.values.get('status'),
        'next_page': int(request.values.get('next_page') or 1)
    }
    kwargs = {
        'status': form.get('status'),
        'limit': page_size,
        'offset': (form.get('next_page')-1)*page_size
    }
    roles = StaffRole.query(**kwargs)
    roles = [r.to_dict() for r in roles]
    # 查询总数
    total_count = StaffRole.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('platform/staff_role_query.html', form=form, roles=roles, statuses=dict(StaffRoleStatus), page=form.get('next_page'), total_count=total_count, total_pages=total_pages)


@blueprint.route('/staff/role/create', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_role_create():
    if request.method == 'GET':
        return render_template('platform/staff_role_create.html', form={})
    else:
        form = {
            'roleno': request.values.get('roleno'),
            'name': request.values.get('name'),
            'abstract': request.values.get('abstract') or ''
        }
        if not all([form.get('roleno'), form.get('name')]):
            return render_template('platform/staff_role_create.html', form=form, msg='角色编号和名称为必填项！')
        if StaffRole.query(roleno=form.get('roleno')):
            return render_template('platform/staff_role_create.html', form=form, msg='角色编号%s已被使用，请重新输入！' % form.get('roleno'))
        role = StaffRole(roleid=utils.uuid1())
        role.roleno = form.get('roleno')
        role.name = form.get('name')
        role.abstract = form.get('abstract')
        role.save()
        # qiyehao_message.send_text('【职工管理】\n\n角色，创建成功!\n\n名称：%s\n编号：%s\n简介：%s' % (role.name, role.roleno, role.abstract))
        return redirect('/%s/platform/staff/role/update?roleid=%s&msg=%s' % (config.appname, role.roleid, '创建成功！'))


@blueprint.route('/staff/role/update', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_role_update():
    role = StaffRole(roleid=request.values.get('roleid'))
    if request.method == 'GET':
        return render_template('platform/staff_role_update.html', form={}, role=role.to_dict(), msg=request.values.get('msg') or '')
    else:
        form = {
            'roleno': request.values.get('roleno'),
            'name': request.values.get('name'),
            'abstract': request.values.get('abstract') or ''
        }
        if not all([form.get('roleno'), form.get('name')]):
            return render_template('platform/staff_role_create.html', form=form, msg='角色编号和名称为必填项！')
        if role.roleno != form.get('roleno') and StaffRole.query(roleno=form.get('roleno')):
            return render_template('platform/staff_role_create.html', form=form, msg='角色编号%s已被使用，请重新输入！' % form.get('roleno'))
        if role.roleno != form.get('roleno'):
            role.roleno = form.get('roleno')
        role.name = form.get('name')
        role.abstract = form.get('abstract')
        role.save()
        # qiyehao_message.send_text('【职工管理】\n\n角色，修改成功!\n\n名称：%s\n编号：%s\n简介：%s' % (role.name, role.roleno, role.abstract))
        return render_template('platform/staff_role_update.html', form=form, role=role.to_dict(), msg='保存成功！')

@blueprint.route('/staff/role/delete', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_role_delete():
    roleid = request.values.get('roleid')
    if not roleid:
        return BadRequest(description='请求参数错误！')
    role = StaffRole(roleid=roleid)
    role.status = StaffRoleStatus.deleted
    role.save()
    return redirect('/%s/platform/staff/role/query' % config.appname)

@blueprint.route('/staff/role/permissions/update', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_role_permissions_update():
    roleid = request.values.get('roleid')
    role = StaffRole(roleid=roleid)
    if not role.exists:
        raise BadRequest(description='该角色不存在！')
    if request.method == 'GET':
        return render_template('platform/staff_role_permissions_update.html', role=role.to_dict(), all_menus=Blueprint.get_allmenus(), msg=request.values.get('msg') or '')
    else:
        form = {
            'permission_urls': request.values.getlist('permission_urls') or []
        }
        role.permission_urls = form.get('permission_urls')
        role.save()
        # # 如果更改默认权限，则更新
        # 暂隐掉默认权限
        # if roleid=='dab2edf080ca11e7bd34a0c589188e1d':
        #     from flask import current_app
        #     current_app.defaultpower = StaffRole.query(roleid=roleid)[0].to_dict().get('permission_urls') or []
        # qiyehao_message.send_text('【职工管理】\n\n角色，权限修改成功!\n\n名称：%s\n编号：%s' % (role.name, role.roleno))
        return redirect('/%s/platform/staff/role/permissions/update?roleid=%s&msg=%s' % (config.appname, role.roleid, '保存成功！'))


@blueprint.route('/staff/post/query', menu_path='平台运营/员工管理/岗位管理', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_post_query():
    page_size = 10
    form = {
        'status': request.values.get('status'),
        'next_page': int(request.values.get('next_page') or 1)
    }
    kwargs = {
        'status': form.get('status'),
        'limit': page_size,
        'offset': (form.get('next_page')-1)*page_size
    }
    posts = StaffPost.query(**kwargs)
    posts = [p.to_dict() for p in posts]
    # 查询总数
    total_count = StaffPost.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('platform/staff_post_query.html', form=form, posts=posts, statuses=dict(StaffPostStatus), page=form.get('next_page'), total_count=total_count, total_pages=total_pages)


@blueprint.route('/staff/post/create', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_post_create():
    if request.method == 'GET':
        return render_template('platform/staff_post_create.html', form={})
    else:
        form = {
            'postno': request.values.get('postno'),
            'name': request.values.get('name'),
            'abstract': request.values.get('abstract') or ''
        }
        if not all([form.get('postno'), form.get('name')]):
            return render_template('platform/staff_post_create.html', form=form, msg='岗位编号和名称为必填项！')
        if StaffPost.query(postno=form.get('postno')):
            return render_template('platform/staff_post_create.html', form=form, msg='岗位编号%s已被使用，请重新输入！' % form.get('postno'))
        post = StaffPost(postid=utils.uuid1())
        post.postno = form.get('postno')
        post.name = form.get('name')
        post.abstract = form.get('abstract')
        post.save()
        # qiyehao_message.send_text('【职工管理】\n\n岗位，创建成功!\n\n名称：%s\n编号：%s\n简介：%s' % (post.name, post.postno, post.abstract))
        return redirect('/%s/platform/staff/post/update?postid=%s&msg=%s' % (config.appname, post.postid, '创建成功！'))


@blueprint.route('/staff/post/update', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_post_update():
    post = StaffPost(postid=request.values.get('postid'))
    if request.method == 'GET':
        return render_template('platform/staff_post_update.html', form={}, post=post.to_dict(), msg=request.values.get('msg') or '')
    else:
        form = {
            'postno': request.values.get('postno'),
            'name': request.values.get('name'),
            'abstract': request.values.get('abstract') or ''
        }
        if not all([form.get('post'), form.get('name')]):
            return render_template('platform/staff_post_create.html', form=form, msg='岗位编号和名称为必填项！')
        if post.postno != form.get('postno') and StaffPost.query(postno=form.get('postno')):
            return render_template('platform/staff_role_create.html', form=form, msg='角色编号%s已被使用，请重新输入！' % form.get('roleno'))
        if post.postno != form.get('postno'):
            post.postno = form.get('postno')
        post.name = form.get('name')
        post.abstract = form.get('abstract')
        post.save()
        # qiyehao_message.send_text('【职工管理】\n\n岗位，修改成功!\n\n名称：%s\n编号：%s\n简介：%s' % (post.name, post.postno, post.abstract))
        return render_template('platform/staff_role_update.html', form=form, post=post.to_dict(), msg='保存成功！')

@blueprint.route('/staff/post/delete', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_post_delete():
    postid = request.values.get('postid')
    if not postid:
        return BadRequest(description='请求参数错误！')
    post = StaffPost(postid=postid)
    post.status = StaffPostStatus.deleted
    post.save()
    return redirect('/%s/platform/staff/post/query' % config.appname)


@blueprint.route('/staff/query', menu_path='平台运营/员工管理/员工列表', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_query():
    page_size = 10
    form = {
        'roleid': request.values.get('roleid'),
        'next_page': int(request.values.get('next_page') or 1)
    }
    kwargs = {
        'roleid': form.get('roleid'),
        'limit': page_size,
        'offset': (form.get('next_page')-1)*page_size
    }
    staffs = Staff.query(**kwargs)
    staffs = [s.to_dict(extra_keys=['roles', 'posts']) for s in staffs]

    roles = StaffRole.query(status=StaffRoleStatus.normal)
    roles = [role.to_dict() for role in roles]
    posts = StaffPost.query(status=StaffPostStatus.normal)
    posts = [post.to_dict() for post in posts]
    orgs = [{}]
    # 查询总数
    total_count = Staff.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('platform/staff_query.html', form=form, staffs=staffs, roles=roles, posts=posts, orgs=orgs, page=form.get('next_page'), total_count=total_count, total_pages=total_pages)


@blueprint.route('/staff/create', methods=['GET'])
@needlogin
def api_platform_staff_create():
    target_uid = request.values.get('target_uid')
    target_user = User(uid=target_uid)
    if not target_user.exists:
        raise BadRequest(description='用户不存在！')
    s = Staff(uid=target_uid)
    s.save()
    # qiyehao_message.send_text('【职工管理】\n\n职工，添加成功!\n\n姓名：%s' % (target_user.name or target_user.nickname))
    return redirect('/%s/platform/staff/query' % (config.appname))

@blueprint.route('/staff/update', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_update():
    target_uid = request.values.get('target_uid')
    target_user = User(uid=target_uid)
    s = Staff(uid=target_uid)
    roles = StaffRole.query(status=StaffRoleStatus.normal)
    roles = [role.to_dict() for role in roles]
    posts = StaffPost.query(status=StaffPostStatus.normal)
    posts = [post.to_dict() for post in posts]
    # 机构相关
    orgs = [{}]
    orgownids = {}
    orgown = [{}]

    if request.method == 'GET':
        return render_template('platform/staff_update.html', form={}, staff=s.to_dict(), roles=roles, posts=posts, orgs=orgs, orgown=orgown, orgownids=orgownids, msg=request.values.get('msg') or '')
    else:
        form = {
            'slogan': request.values.get('slogan'),
            'photo': request.values.get('photo') or target_user.avatar,
            'roleids': request.values.getlist('roleids'),
            'postids': request.values.getlist('postids'),
            'introduction': request.values.get('introduction')
        }
        # 老的roleids和岗位ids
        old_roleids = copy.deepcopy(s.roleids or [])
        old_postids = copy.deepcopy(s.postids or [])

        s.slogan = form.get('slogan')
        s.photo = form.get('photo')
        s.roleids = form.get('roleids') or []
        s.postids = form.get('postids') or []
        s.introduction = form.get('introduction')
        s.save()

        # 最新角色信息
        now_roles = '，'.join([role.get('name') for role in s.roles])
        # 新增角色信息
        removed_roleids = list(set(old_roleids).difference(set(s.roleids or [])))
        removed_roles = '，'.join([role.name for role in StaffRole.query(roleid=removed_roleids)]) if removed_roleids else '无'
        # 删除角色信息
        added_roleids = list(set(s.roleids or []).difference(set(old_roleids)))
        added_roles = '，'.join([role.name for role in StaffRole.query(roleid=added_roleids)]) if added_roleids else '无'

        # 最新岗位信息
        now_posts = '，'.join([post.get('name') for post in s.posts])
        # 新增岗位信息
        removed_postids = list(set(old_postids).difference(set(s.postids or [])))
        removed_posts = '，'.join([post.name for post in StaffPost.query(postid=removed_postids)]) if removed_postids else '无'
        # 删除角色信息
        added_postids = list(set(s.postids or []).difference(set(old_postids)))
        added_posts = '，'.join([post.name for post in StaffPost.query(postid=added_postids)]) if added_postids else '无'

        # qiyehao_message.send_text('【职工管理】\n\n职工，修改成功!\n\n姓名：%s\n\n角色：%s\n新增角色：%s\n删除角色：%s\n\n岗位：%s\n新增岗位：%s\n删除岗位：%s' % (target_user.name or target_user.nickname, now_roles, added_roles, removed_roles, now_posts, added_posts, removed_posts))
        return redirect('/%s/platform/staff/update?target_uid=%s&msg=%s' % (config.appname, target_uid, '保存成功！'))

@blueprint.route('/staff/delete', methods=['GET', 'POST'])
@needlogin
def api_platform_staff_delete():
    target_uid = request.values.get('target_uid')
    s = Staff(uid=target_uid)
    orglist = []
    orglist.append(s)
    RDSLibModel.delete_all(*orglist)
    return redirect('/%s/platform/staff/query' % (config.appname))
