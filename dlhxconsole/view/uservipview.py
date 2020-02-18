# -*- coding: utf-8 -*-
from flask import Flask, Blueprint, request, render_template
from xdock.bases import json, utils, config, logging
from xdock_user.lib import User
from xdock_user.lib.user import UserVip

logger = logging.getLogger('console.user.vip')

blueprint = Blueprint('console.user.vip', __name__, url_prefix='/uservip')


@blueprint.route('/query', methods=['GET', 'POST'])
def api_uservip_query():
    page_size = 30
    form = {
        'expired': request.values.get('expired'),
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size
    }
    kwargs = {
        'expired': form.get('expired'),
        'limit': page_size,
        'offset': (form['next_page'] - 1) * page_size
    }
    uservipslist = []
    for uservip in UserVip.query(**kwargs):
        user = User(uid=uservip.uid)
        uservip = uservip.to_dict()
        uservip['user'] = user.to_dict()
        uservipslist.append(uservip)
    # 查询总数
    total_count = UserVip.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size
    return render_template('uservip/uservip_query.html', form=form, total_count=total_count, uservips=uservipslist, total_pages=total_pages, page=form.get('next_page'))

