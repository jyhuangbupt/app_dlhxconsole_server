# -*- coding: utf-8 -*-
'''控制台HNKView'''

import xlrd, time
import flask_excel as excel #下载excel
import sys, traceback, datetime, random
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import apphelper, NotAllowed, BadRequest, TooFrequently, SmsCodeError, NotFound
from xdock.apps import XDockBlueprint as Blueprint
from xdock.yunqq.qiyehao import qiyehao_message
from xdock_jiamei.lib.order import *
from xdock_jiamei.lib.vip import *
from xdock_jiamei.lib.product import *
from . import needlogin
logger = logging.getLogger('Console.jiamei.order')

blueprint = Blueprint('console.jiamei.order', __name__, url_prefix='/order')

@blueprint.route('', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
def api_index():
    return render_template('order/index.html')



@blueprint.route('/query', methods=['GET', 'POST'])
@needlogin
def api_jiamei_order_query():
    '''查询订单列表'''
    page_size = 20
    status = request.values.get('status') or ''
    ordertype = request.values.get('type') or ''
    phone = request.values.get('phone') or ''
    startdate = request.values.get('startdate') or ''
    endtdate = request.values.get('enddate') or ''
    form = {
        'phone': phone,
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size,
        'status': status,
        'startdate': startdate,
        'enddate': endtdate,
        'type': ordertype
    }
    kwargs = {
        'offset': (form['next_page'] - 1) * page_size,
        'phone': phone,
        'limit': page_size,
        'status': status,
        'startdate': startdate,
        'enddate': endtdate,
        'type': ordertype
    }
    orderlist = Order.query(**kwargs)
    orderlist = [o.to_dict() for o in orderlist]
    # 查询总数
    total_count = Order.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size

    return render_template('order/order_list.html', OrderStatus=OrderStatus, form=form, orders=orderlist,
                           page=form['next_page'], total_pages=total_pages, total_count=total_count)
@blueprint.route('/order/cancel', methods=['GET', 'POST'])
@needlogin
def api_jiamei_order_cancel():
    '''取消订单'''
    orderid = request.values.get('orderid') or ''
    if not orderid:
        raise BadRequest(description='订单号错误！')
    order = Order(orderid=orderid)
    if not order:
        raise BadRequest(description='订单不存在！')
    if order.status == OrderStatus.canceledbyoperator or order.status==OrderStatus.canceled:
        raise BadRequest(description='此订单已取消，不可多次取消！')
    order.status = OrderStatus.canceledbyoperator
    order.save()
    uid = order.uid
    # 回滚产品
    for p in order.products:
        vipCard = VipCard.query(productid=p['productid'])
        vip = JiameiVip.query(uid=uid, cardid=vipCard[0].cardid)
        vip[0].remain = vip[0].remain + p['count']
        vip[0].save()
    try:
        timearr = str(order.shouhuo_time).split(' ')[0].split('-')
        qiyehao_message.send_text("【运营取消订单】\n\n运营取消订单成功！\n\n订单号：%s\n收货人：%s\n收货时间：%s\n会员信息：%s" % (order.orderid,order.shouhuo_name+' '+order.shouhuo_phone, str(timearr[0])+'年'+str(timearr[1])+'月'+str(timearr[2])+'日', order.name+" "+order.phone), group='order')
    except:
        pass
    return apphelper.format_ok_response(data={'data': {'status': 'ok'}})


@blueprint.route('/preorder/cancel', methods=['GET', 'POST'])
@needlogin
def api_jiamei_preorder_cancel():
    '''取消自动发货订单'''
    uid = request.values.get('uid') or ''
    if not uid:
        raise BadRequest(description='该会员不存在！')
    preorder = PreOrder.query(uid=uid)
    preorder[0].status = 'canceled'
    preorder[0].save()
    return apphelper.format_ok_response(data={'data': {'status': 'ok'}})

@blueprint.route('excel/export', methods=['GET'])
@needlogin
def api_jiamei_order_export():
    '''查询订单列表'''
    page_size = 1000
    status = request.values.get('status') or ''
    ordertype = request.values.get('type') or ''
    phone = request.values.get('phone') or ''
    startdate = request.values.get('startdate') or ''
    endtdate = request.values.get('enddate') or ''
    form = {
        'phone': phone,
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size,
        'status': status,
        'startdate': startdate,
        'enddate': endtdate,
        'type': ordertype
    }
    kwargs = {
        'offset': (form['next_page'] - 1) * page_size,
        'phone': phone,
        'limit': page_size,
        'status': status,
        'startdate': startdate,
        'enddate': endtdate,
        'type': ordertype
    }
    orderlist = Order.query(**kwargs)
    orders = [[
        '订单号',
        '订单名称',
        '会员姓名',
        '会员手机',
        '收货姓名',
        '收货电话',
        '收货时间',
        '收货地址',
        '产品及份数',
        '订单状态',
        '订单备注',
        '发货时间',
        '快递单号',
        '下单时间',
        '下单类型'
    ]]
    if len(orderlist)>0:
        for order in orderlist:
            try:
                test = order.shouhuo_address['district']
                try:
                    shouhuo_address = (order.shouhuo_address['district']['province'] or "") + (order.shouhuo_address['district']['city'] or "") + (order.shouhuo_address['district']['area'] or "") + (order.shouhuo_address['district']['town'] or "") + (order.shouhuo_address['address'] or "")
                except:
                    shouhuo_address = (order.shouhuo_address['district']['province'] or "")+(order.shouhuo_address['district']['city'] or "") + (order.shouhuo_address['district']['area'] or "") + (order.shouhuo_address['address'] or "")
            except:
                shouhuo_address = "无"
            products = ''
            for p in order.products:
                products = products + p['name'] + '*' + str(p['count']) + '份;'

            o = [
                order.orderid,
                order.order_name,
                (order.user['name'] or order.user['nickname']),
                order.user['phone'],
                order.shouhuo_name,
                order.shouhuo_phone,
                order.shouhuo_time.strftime("%Y-%m-%d %H:%M:%S")[0:10],
                shouhuo_address,
                products,
                OrderStatus[order.status],
                order.note,
                order.wuliu_time[0:10],
                order.wuliu_number,
                order.ct,
                '自动下单' if order.type == 'auto' else '手动下单'
            ]
            orders.append(o)
            now = int(time.time())
            timeArray = time.localtime(now)
            otherStyleTime = time.strftime("%Y.%m.%d_%H.%M", timeArray)
            filename = 'order_'+otherStyleTime
    return excel.make_response_from_array(orders, "xlsx", file_name=filename)

@blueprint.route('/excel/upload', methods=['GET', 'POST'])
@needlogin
def api_jiamei_order_upload():
    if request.method == 'POST':
        file = request.files['file']
        f = file.read()
        data = xlrd.open_workbook(file_contents=f)
        table = data.sheets()[0]
        names = data.sheet_names()  # 返回book中所有工作表的名字
        status = data.sheet_loaded(names[0])  # 检查sheet1是否导入完毕
        print(status)
        nrows = table.nrows  # 获取该sheet中的有效行数
        ncols = table.ncols  # 获取该sheet中的有效列数
        print(nrows)
        print(ncols)
        for index in range(1, nrows, 1):
            # [订单号", "订单名称", "会员姓名", "会员手机", "收货姓名", "收货电话", "收货时间", "收货地址", "产品及份数", "订单状态", "订单备注", "发货时间", "快递单号"]
            o = table.row_values(index)  # 第1列数据
            order = Order.query(orderid=o[0])
            if len(order) < 1:
                return render_template('order/order_upload.html', message='订单更新失败，未查询到订单，请检查第'+str(index)+'行订单号是否正确')
        #     更新发货时间，快递单号，其他不更新
            if o[9] == '已发货':
                order[0].status = OrderStatus.sended
            elif o[9] == '已完成':
                order[0].status = OrderStatus.finished
            order[0].wuliu_time = o[11]
            order[0].wuliu_number = o[12]
            order[0].save()
        return render_template('order/order_upload.html', message='订单更新成功')
    return render_template('order/order_upload.html')

@blueprint.route('/starttime', methods=['GET', 'POST'])
@needlogin
def api_jiamei_order_starttime():
    if request.method == 'POST':
        starttime = request.values.get('starttime')
        disabledtime = request.values.get('disabledtime')
        time = OrderStartTime(timeid='starttimeid')
        time.time = starttime
        time.disabledtime = disabledtime
        time.save()
        return render_template('order/order_start_time.html', starttime=starttime, disabledtime=disabledtime, message='设置成功')
    else:
        time = OrderStartTime(timeid='starttimeid')
        time = time.to_dict()
        starttime = time['time_ui'][0:10]
        return render_template('order/order_start_time.html', starttime=starttime, disabledtime=time['disabledtime'])

