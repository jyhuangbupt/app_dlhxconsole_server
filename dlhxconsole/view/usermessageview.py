# -*- coding: utf-8 -*-
import sys, traceback, datetime
from flask import Flask, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import NotAllowed, NotFound, BadRequest
from xdock.apps import XDockBlueprint as Blueprint
from xdock.yunqq.qiyehao import qiyehao_message
from xdock_user.lib.usermessage import UserMessage2Template

logger = logging.getLogger('console.faly.usermessage.view')

blueprint = Blueprint('console.faly.usermessage', __name__, url_prefix='/usermessage')

@blueprint.route('', methods=['GET', 'POST'])
def api_index():
    return render_template('platform/index.html')


@blueprint.route('/template/query', methods=['GET', 'POST'])
def api_usermessage_template_query():
    page_size = 20
    form = {
        'name': request.values.get('name' or ''),
        # 'isconsolesms': request.values.get('isconsolesms') or 'false' if request.method == 'POST' else 'true',
        'isconsolesms': 'false',
        'next_page': int(request.values.get('next_page') or 1)
    }
    kwargs = {
        'name': form.get('name'),
        'isconsolesms': form.get('isconsolesms'),
        'limit': page_size,
        'offset': (form.get('next_page') - 1) * page_size
    }
    templates = UserMessage2Template.query(**kwargs)
    templates = [t.to_dict() for t in templates]
    total_count = UserMessage2Template.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('platform/usermessage_template_query.html', templates=templates, total_count=total_count, total_pages=total_pages, page=form.get('next_page'), form=form)


@blueprint.route('/template/create', methods=['GET', 'POST'])
def api_usermessage_template_create():
    if request.method == 'GET':
        return render_template('platform/usermessage_template_create.html', form={}, msg=request.values.get('msg', ''))
    else:
        form = {
            'name': request.values.get('name'),
            'messageid': request.values.get('messageid', ''),
            'sms_template': request.values.get('sms_template', ''),
            'weixin_template_id': request.values.get('weixin_template_id', ''),
            'weixinminiapp_template_id': request.values.get('weixinminiapp_template_id', ''),
            'isconsolesms': 'true' if request.values.get('isconsolesms') else 'false'
        }
        if form['messageid'] and UserMessage2Template.from_messageid(messageid=form['messageid']):
            return render_template('platform/usermessage_template_create.html', form=form, msg='此消息ID已存在')
        t = UserMessage2Template(templateid=utils.uuid1(), **form)
        t.save()
        return redirect('/%s/usermessage/template/update?templateid=%s&msg=%s' % (config.appname, t.templateid, u'创建成功'))


@blueprint.route('/template/update', methods=['GET', 'POST'])
def api_usermessage_template_update():
    t = UserMessage2Template(templateid=request.values.get('templateid'))
    if request.method == 'GET':
        return render_template('platform/usermessage_template_update.html', form=t.to_dict(), msg=request.values.get('msg', ''))
    else:
        form = {
            'templateid': request.values.get('templateid'),
            'name': request.values.get('name'),
            'messageid': request.values.get('messageid') or None,
            'sms_template': request.values.get('sms_template', ''),
            'weixin_template_id': request.values.get('weixin_template_id', ''),
            'weixinminiapp_template_id': request.values.get('weixinminiapp_template_id', ''),
            'isconsolesms': 'true' if request.values.get('isconsolesms') else 'false'
        }
        if form['messageid'] and UserMessage2Template.from_messageid(messageid=form['messageid'], exclude=t.templateid):
            return render_template('platform/usermessage_template_update.html', form=form, msg='此消息ID已存在')
        t.update(**form)
        return redirect('/%s/usermessage/template/update?templateid=%s&msg=%s' % (config.appname, t.templateid, u'更新成功'))


@blueprint.route('/template/delete', methods=['GET', 'POST'])
def api_usermessage_template_delete_ajax():
    templateid = request.values.get('templateid')
    if not templateid:
        raise BadRequest(description='请求参数错误!')
    t = UserMessage2Template(templateid=templateid)
    t.delete()
    return redirect('/%s/usermessage/template/query' % config.appname)
