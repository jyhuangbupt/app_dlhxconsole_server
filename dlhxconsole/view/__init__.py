# -*- coding: utf-8 -*-
import functools

from flask import session, request, redirect
from xdock.bases import config


def needlogin(f):
    '''当一个View需要检查用户是否登录信息时，请明确使用此装饰器'''
    @functools.wraps(f)
    def _wraps(*args, **kwargs):
        phone = session.get('phone', None)
        if not phone:
            # 没有登录或者session已经过期
            session['access_url'] = request.url
            return redirect('/%s/user/login' % config.appname)
        return f(*args, **kwargs)
    return _wraps

