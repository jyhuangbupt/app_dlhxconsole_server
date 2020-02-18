# -*- coding: utf-8 -*-
'''文件及图片管理'''

from flask import Blueprint, request, json
from xdock.bases import json, logging
from xdock.apps import apphelper, BadRequest
from xdock_jiamei.lib.file import FalyImageFile

logger = logging.getLogger('faly.view.file')

blueprint = Blueprint('faly.view.file', __name__, url_prefix='/resource')

@blueprint.route('/image/simditor/upload/ajax', methods=['GET', 'POST'])
@blueprint.route('/simditor/image/upload/ajax', methods=['GET', 'POST'])
def api_simditor_image_upload_ajax():
    name = request.form.get('name') or ''
    tag = request.form.get('tag') or ''
    width = request.values.get('width')
    f = request.files.get('image-file') or request.files.get('filedata')
    if not f:
        return apphelper.format_str_response(json.dumps({
            'success': False,
            'msg': '上传图片失败，无法读取文件信息！'
            }))
    f = FalyImageFile.upload(f, tag=tag, name=name or f.filename, filename=f.filename, rename=True)
    data = {
        'success': True,
        'msg': '上传图片成功！',
        'file_path': f.url if f.url.endswith('.gif') else (f.urls.get('640w') if not width else '%s?x-oss-process=image/resize,w_%s' % (f.url, width))
    }
    return apphelper.format_str_response(json.dumps(data))


@blueprint.route('/jquery/fileupload/ajax', methods=['GET', 'POST'])
def api_jquery_fileupload_ajax():
    name = request.form.get('name') or ''
    tag = request.form.get('tag') or ''
    width = request.values.get('width')
    f = request.files.get('image-file') or request.files.get('uploadfile') or request.files.values[0]
    if not f:
        return apphelper.format_str_response(json.dumps({
            'success': False,
            'msg': '上传文件失败，无法读取文件信息！'
            }))
    f = FalyImageFile.upload(f, tag=tag, name=name or f.filename, filename=f.filename, rename=True)
    return apphelper.format_str_response(json.dumps({
        'success': True,
        'msg': '上传文件成功！',
        'file_url': f.url if not width else '%s?x-oss-process=image/resize,w_%s' % (f.url, width),
        'file_name': f.name,
        'file_size': request.values.get('uploadsize')
        }))

@blueprint.route('/tools/file/upload/ajax', methods=['GET', 'POST'])
@blueprint.route('/tools/image/upload/ajax', methods=['GET', 'POST'])
def api_tools_image_upload_ajax():
    name = request.form.get('name') or ''
    tag = request.form.get('tag') or ''
    width = request.values.get('width')
    f = request.files.get('image-file')
    if not f:
        raise BadRequest(description='请选择要上传的文件')

    filename = f.filename if '.' in f.filename else name
    f = FalyImageFile.upload(f, tag=tag, name=name or f.filename, filename=filename, rename=True)
    data = {
        'url': f.url,
        'file_url': f.url,
        'file_path': f.url,
    }
    data.update(f.urls)
    if width:
        data.update({
            width: '%s?x-oss-process=image/resize,w_%s' % (f.url, width)
        })
    return apphelper.format_ok_response(data=data)


@blueprint.route('/tools/video/upload/ajax', methods=['GET', 'POST'])
def api_tools_video_upload_ajax():
    name = request.form.get('name') or ''
    tag = request.form.get('tag') or ''
    f = request.files.get('video-file')
    if not f:
        raise BadRequest(description='请选择要上传的文件')

    f = FalyImageFile.upload(f, tag=tag, name=name or f.filename, filename=f.filename, rename=True)
    data = {
        'url': f.url,
        'file_url': f.url,
        'file_path': f.url,
    }
    data.update(f.urls)
    return apphelper.format_ok_response(data=data)


@blueprint.route('/tools/audio/upload/ajax', methods=['GET', 'POST'])
def api_tools_audio_upload_ajax():
    name = request.form.get('name') or ''
    tag = request.form.get('tag') or ''
    f = request.files.get('audio-file')
    if not f:
        raise BadRequest(description='请选择要上传的文件')

    f = FalyImageFile.upload(f, tag=tag, name=name or f.filename, filename=f.filename, rename=True)
    data = {
        'url': f.url,
        'file_url': f.url,
        'file_path': f.url,
    }
    data.update(f.urls)
    return apphelper.format_ok_response(data=data)
