# -*- coding: utf-8 -*-
'''控制台productView'''
import time

import sys, traceback, datetime, random
from flask import Flask, Blueprint, request, session, g, json, jsonify, render_template, make_response, url_for, redirect
from xdock.bases import json, utils, config, logging
from xdock.apps import apphelper, NotAllowed, BadRequest, TooFrequently, SmsCodeError, NotFound
from xdock.apps import XDockBlueprint as Blueprint
from xdock_jiamei.lib.product import *
from . import needlogin
logger = logging.getLogger('Console.jiamei.product')

blueprint = Blueprint('console.jiamei.product', __name__, url_prefix='/platform')

@blueprint.route('', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
def api_index():
    return render_template('hnk/index.html')



@blueprint.route('/product/query', menu_path='平台运营/产品管理/产品列表', methods=['GET', 'POST'])
@needlogin
def api_jiamei_product():
    '''产品列表'''
    page_size = 20
    form = {
        'name': request.values.get('name'),
        'next_page': int(request.values.get('next_page') or 1),
        'limit': page_size,
        # 'status': ProductStatus.published
    }
    kwargs = {
        'name': form.get('name'),
        'limit': page_size,
        'offset': (form['next_page'] - 1) * page_size,
    }
    productlist = Product.query(**kwargs)
    productlist = [p.to_dict() for p in productlist]
    # 查询总数
    total_count = Product.query(count=True, **kwargs)
    total_pages = (total_count + page_size - 1) / page_size

    return render_template('platform/product_query.html', ProductStatus=ProductStatus, form=form, products=productlist,
                           page=form['next_page'], total_pages=total_pages, total_count=total_count)


@blueprint.route('/product/offset/ajax', methods=['GET', 'POST'])
@needlogin
def api_hnk_product_offset_ajax():
    '''游学产品下架'''
    product = Product(productid=request.values.get('productid'))
    if not product.exists:
        raise BadRequest(description='该内容不存在！')
    if product.status == ProductStatus.published:
        product.status = ProductStatus.editing
        product.save()
    return apphelper.format_ok_response()

@blueprint.route('/product/publish/ajax', methods=['GET', 'POST'])
@needlogin
def api_hnk_product_publish_ajax():
    '''游学产品上架'''
    product = Product(productid=request.values.get('productid'))
    if not product.exists:
        raise BadRequest(description='该内容不存在！')
    if product.status == ProductStatus.editing:
        product.status = ProductStatus.published
        product.save()
    return apphelper.format_ok_response()


@blueprint.route('/product/stick/ajax', methods=['POST'])
@needlogin
def api_product_stick_ajax():
    product = Product(productid=request.values.get('productid'))
    if not product.exists:
        raise BadRequest(description='该内容不存在！')

    product.ot = int(time.time()*1000)
    product.save()
    return apphelper.format_ok_response()


@blueprint.route('/product/delete/ajax', methods=['POST'])
@needlogin
def api_product_delete_ajax():
    productid = request.values.get('productid')
    product = Product(productid=productid)
    if product.exists:
        product.delete()
    return apphelper.format_ok_response()

@blueprint.route('/product/update', menu_path='平台运营/产品管理/产品创建', methods=['GET', 'POST'])
@needlogin
def api_product_update():
    if request.method == 'GET':
        productid = request.values.get('productid')
        product = Product(productid=productid)
        return render_template('platform/product_update.html', product=product.to_dict() if product else {})
    else:
        productid = request.values.get('productid')
        if not productid:
            count = Product.query(count=True)
            product = Product(productid=utils.uuid1())
            product.product_num = 'PRODUCT'+str(count+1)
            product.status = ProductStatus.editing
            product.ot = int(time.time() * 1000)
        else:
            product = Product(productid=productid)
        product.name = request.values.get('name')
        product.cover = request.values.get('cover')
        product.tip = request.values.get('tip')
        product.abstract = request.values.get('abstract')
        product.save()
        return apphelper.format_ok_response()
