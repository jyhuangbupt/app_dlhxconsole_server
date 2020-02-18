# -*- coding: utf-8 -*-
import sys, traceback, datetime
from flask import Flask, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import NotAllowed, NotFound, BadRequest
from xdock_user.lib import User, UserRDS
from xdock.apps import XDockBlueprint as Blueprint

logger = logging.getLogger('console.dlhx.common.view')

blueprint = Blueprint('console.faly.common', __name__, url_prefix='/common')


@blueprint.route('/result', methods=['GET'])
def api_common_result():
    return render_template('result.html', title=request.values.get('title') or '', type=request.values.get('type') or '', message=request.values.get('message') or '', description=request.values.get('description') or '', redirect_url=request.values.get('redirect_url') or '')


@blueprint.route('/user/select', menu_path='平台运营/员工管理/员工查询', methods=['GET', 'POST'])
def api_common_user_select():
    temp = request.query_string.split('?')

    form = {
        'name': request.values.get('name'),
        'redirect_url': temp[0].split('=')[1],
        'redirect_url_query_string': temp[1] if len(temp) > 1 else '',
        'query_all': request.values.get('query_all')
    }

    if form.get('name'):
        kwargs = {}
        try:
            int(form.get('name'))
        except:
            kwargs['name'] = form.get('name')
        else:
            if len(form.get('name')) == 11:
                kwargs['phone'] = form.get('name')
            else:
                kwargs['uid'] = form.get('name')
        users = UserRDS.query(limit=None, offset=None, **kwargs)
        users = [User(uid=u.uid).to_dict() for u in users]
    else:
        users = []
    return render_template('common/user_select.html', users=users, form=form)
