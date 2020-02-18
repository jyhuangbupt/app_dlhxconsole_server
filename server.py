# -*- coding: utf-8 -*-

import sys, os
from flask import session, g, request, Blueprint, redirect, render_template
from xdock.bases import config, logging, logger
from xdock.apps import apphelper, NotAllowed, BadRequest
from xdock.apps import apphelper, XDockAdminApp, set_app
import flask_excel as excel

app = XDockAdminApp(__name__, static_folder='dlhxconsole/static', static_url_path='/%s/static' % config.appname, template_folder='dlhxconsole/templates')
excel.init_excel(app)
set_app(app)

blueprint = Blueprint('console', __name__)

@blueprint.route('/%s' % config.appname, methods=['GET'])
def api_home():
    return redirect('/%s/user/query?target_uid=%s' % (config.appname, g.user.uid))

app.mount([blueprint])


# 工具界面
from dlhxconsole.view.utilsview import blueprint as utilsview_blueprint
app.mount([utilsview_blueprint], prefix={utilsview_blueprint.name: '/%s' % config.appname})

# 文件上传接口
from dlhxconsole.view.fileview import blueprint as fileview_blueprint
app.mount([fileview_blueprint], prefix={fileview_blueprint.name: '/%s' % config.appname})

# 产品接口
from dlhxconsole.view.productview import blueprint as productview_blueprint
app.mount([productview_blueprint], prefix={productview_blueprint.name: '/%s' % config.appname})

# 用户消息管理
from dlhxconsole.view.usermessageview import blueprint as usermessageview_blueprint
app.mount([usermessageview_blueprint], prefix={usermessageview_blueprint.name: '/%s' % config.appname})

# 通用界面
from dlhxconsole.view.commonview import blueprint as commonview_blueprint
app.mount([commonview_blueprint], prefix={commonview_blueprint.name: '/%s' % config.appname})




if __name__ == '__main__':
    app.run()