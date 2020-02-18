/**
 * 关于XDock运行环境
 */

function XDock() {

    var _xdock = {'config': {}};
    _xdock.init = function() {
        //初始化session中设置的KV为xdock的属性
        $('._session').each(function() {
            var v = $(this).val();
            if (v.toLowerCase() == 'true') {
                v = true;
            } else if (v.toLowerCase() == 'false') {
                v = false;
            }
            _xdock.config[$(this).attr('id').substring(9)] = v;
        });
        //初始化返回按钮
        //TODO: 后面还应该跟浏览器禁用回退事件结合起来。
        $('#_return').click(function() {
            var _returnurl = $(this).find('input:first').val();
            $(this).find('input:first').val('');
            if (_returnurl != null && _returnurl.trim() != '') {
                window.location.href = _returnurl;
            } else {
                window.history.go(-1);
            }
        });
        //初始化所有的可点击按钮和菜单
        $('.item-click').each(function() {
            $(this).click(function(e) {
                var url = $(this).find('input:first').val();
                if (url != '' && url != undefined) {
                    _xdock.showloading();
                    window.location.href = url;
                } else {
                    _xdock.showtoast('平台研发中，敬请期待！')
                }
            })
        });
        //初始化所有的上传裁切照片的表单
        $('.form-photoclip').each(function() {
            var _this = $(this);
            $(this).find('.form-photoclip-btn').first().click(function() {
                _this.find('.form-photoclip-file').first().click();
            });
            var params = $.parseJSON( _this.find('.form-photoclip-panel').first().attr('data-custom'));
             _this.find('.form-photoclip-panel').first().show();
            var cliparea_width =  _this.find('.form-photoclip-panel').first().width();
             _this.find('.form-photoclip-panel').first().hide();
            var cliparea_height = cliparea_width/(params.outer_scale || 1);
            var per_width = params.shortside_percent || 0.85, per_height = params.shortside_percent || 0.85;
            if (cliparea_width <= cliparea_height) {
                per_height = cliparea_width * per_width / (params.inner_scale || 1) / cliparea_height;
            } else {
                per_width = cliparea_height * per_height * (params.inner_scale || 1) / cliparea_width;
            }
            _xdock.clipinit({
                file: _this.find('.form-photoclip-file').first(),
                clippanel:  _this.find('.form-photoclip-panel').first(),
                cliparea_height: cliparea_height + 'px',
                per_width: per_width*100 + '%',
                per_height: per_height*100 + '%',
                outputSize: params.output_size,
                done_func: function (data) {
                    _xdock.hideloading();
                    _xdock.showtoast('上传成功');
                    _this.find('.form-photoclip-text').first().val(data.data.file_url).focus();
                }
            });
        });
        // <div class="form-group form-photoclip" style="margin: 0;">
        //     <label>精致头像</label>
        //     <div class="input-group" style="width: 80%">
        //         <input type="text" class="form-control form-photoclip-text" placeholder="图片地址或者点击右侧选择" style="">
        //         <div class="input-group-addon form-photoclip-btn">+</div>
        //     </div>
        //     <input class="form-photoclip-file" type='file' accept="image/jpeg,image/png,image/bmp">
        //     <p class="help-block" style="">支持.jpg .jepg .bmp .png,大小不超过5M</p>
        //     <div class="form-photoclip-panel" style="display: none; width: 60%" data-custom='{"outer_scale": 1.6, "inner_scale": 1, "output_size": [200,200]}'></div>
        // </div>
        //初始化所有的上传裁切照片的表单 end

        //初始化所有的上传文件的表单
        $('.form-photo').each(function() {
            var _this = $(this);
            $(this).find('.form-photo-btn').first().click(function() {
                _this.find('.form-photo-file').first().click();
            });
            _this.find('.form-photo-file').first().AjaxFileUpload({
                action: '/' + _xdock.config.appname + '/resource/jquery/fileupload/ajax',
                onChange: function(filename) { _xdock.showloading(); },
                onComplete: function(filename, data) {
                    _xdock.hideloading();
                    if (data.success == true) {
                        $(_this).find('.form-photo-text').first().val(data.file_url).focus();
                        $(_this).find('.form-photo-panel').first().empty();
                        $(_this).find('.form-photo-panel').first().append('<img style="width:100%;" src="' + data.file_url + '" />');
                        $(_this).find('.form-photo-panel').first().show();
                        _xdock.showtoast(data.msg);
                    } else {_xdock.showtoast(data.msg); }
                },
            });
            // 使用例子
            // <div class="form-group form-photo" style="margin: 0; margin-top: 10px;">
            //     <label>精致头像</label>
            //     <div class="input-group" style="width: 80%">
            //         <input type="text" class="form-control form-photo-text" placeholder="图片地址或者点击右侧选择" style="">
            //         <div class="input-group-addon form-photo-btn">+</div>
            //     </div>
            //     <input class="form-photo-file" name="image-file" type='file' accept="image/jpeg,image/png,image/bmp">
            //     <p class="help-block" style="">支持.jpg .jepg .bmp .png,大小不超过5M</p>
            //     <div class="form-photo-panel" style="display: none; width: 30%" ></div>
            // </div>
            // 初始化所有的上传文件的表单 end

        });
        //初始化所有的上传照片的表单 end

    }
    //常用操作函数

    //是否是微信浏览器
    _xdock.isWeixinBrowser = navigator.userAgent.toLowerCase().match(/MicroMessenger/i) == 'micromessenger';
    //是否是中文
    _xdock.ischinese = function(string) {
        var re = /[^u4e00-u9fa5]/;
        if (re.test(string)) {
            return true;
        }
        return false;
    }
    /**
     * 将数值四舍五入(保留2位小数)后格式化成金额形式
     * @param num 数值(Number或者String)
     * @return 金额格式的字符串,如'1,234,567.45'
     * @type String
     */
    _xdock.formatcurrency = function(num) {
        num = num.toString().replace(/\$|\,/g, '');
        if (isNaN(num)) {
            num = "0";
        }
        sign = (num == (num = Math.abs(num)));
        num = Math.floor(num * 100 + 0.50000000001);
        cents = num % 100;
        num = Math.floor(num / 100).toString();
        if (cents < 10) {
            cents = "0" + cents;
        }
        for (var i = 0; i < Math.floor((num.length - (1 + i)) / 3); i++) {
            num = num.substring(0, num.length - (4 * i + 3)) + ',' + num.substring(num.length - (4 * i + 3));
        }
        return (((sign) ? '' : '-') + num + '.' + cents);
    }

    /**
     * 展示一个会自动消失的提示信息，简称toast，3秒自动消失。
     */
    _xdock.showtoast = function(msg, color) {
        if (color == null || color == '') {
            color = '#fafafa';
        }
        var p = $('#_showtoast').find('p').first();
        p.text(msg);
        p.css('color', color);
        $('#_showtoast').show()
        setTimeout(function () {
            $('#_showtoast').hide();
        }, 3000);
    }
    _xdock.showloading = function() {
        $('#_showloading').show();
    }
    _xdock.hideloading = function() {
        $('#_showloading').hide();
    }
    _xdock.showphotos = function(photolist, width) {
        var str = '';
        for(var p in photolist){
            str += '<img style="width: '+width+'" src="'+photolist[p]+'" />';
        };
        $("#_showphotos").find('div._photosalbum').first().html(str);
        $('')
        $('#_showphotos').toggle();
        $('body').css('overflow', 'hidden');
    }
    /**
    * 通用ajax请求方法
    */
    _xdock.ajax = function(url, data, success, failure) {
        $.ajax({
            url: url, data: data, type: 'post', dataType: 'json',
            success: function(data) {
                if (data.meta.code == 200) {
                    if (success != null) { success(data.data); }
                } else if (data.meta.code==400 && data.meta.message=='NeedLogin') {
                    _xdock.showloading();
                    _xdock.showtoast('正在跳转到登录界面...');
                    //跳转到登录界面
                    window.location.href = "/" + _xdock.config.appname + "/user/signup?_rdurl=" + encodeURIComponent(window.location);
                } else {
                    if (failure != null) { failure(data.meta) }
                }
            },
            error: function() {
              _xdock.showtoast('网络错误，请稍后重试！');
              if (failure != null) { failure({'code': 400, 'message': '网络错误！'}); }
            }
        });
    }
    //通用更新用户信息接口
    _xdock.userUpdate = function(data, success, failure) {
        _xdock.ajax("/" + _xdock.config.appname + "/user/update/ajax", data)
    }
    //检查当前用户是否已经登录
    _xdock.needLogin = function() {
        if (!_xdock.config.is_user_login) {
            _xdock.showloading();
            _xdock.showtoast('正在跳转到登录界面...');
            //跳转到登录界面
            window.location.href = "/" + _xdock.config.appname + "/user/signup?_rdurl=" + encodeURIComponent(window.location);
        }
    }
    //设置返回按钮
    _xdock.setReturn = function(url) {
        $('#_return').find('input:first').val(url);
    }

    // 裁剪插件
    _xdock.clipinit = function(params){
        /**
         * 参数说明：
            file: <input type="file"> jquery dom object
            clippanel: 包含裁剪插件的父div容器jquery dom object
            cliparea_height: 裁剪差价高度，默认200px
            width：裁剪区域的宽度，固定值，如：200
            height：裁剪区域的高度，固定值，如：200
            per_width: 裁剪区域的宽度，百分比，如：60%；当设置了该项，width不再起作用
            per_height: 裁剪区域的高度，百分比，如：80%；当设置了该项，height不再起作用
            outputSize: 输出图像大小。
                        当值为数字时，表示输出宽度，此时高度根据截取框比例自适应。
                        当值为数组时，数组中索引 [0] 和 [1] 所对应的值分别表示宽和高，若宽或高有一项值无效，则会根据另一项等比自适应。
                        默认值为[0,0]，表示输出图像原始大小。
            start_func: 开始上传图片方法
            complete_func: 完成上传图片后的方法
            done_func: 裁剪完成后方法

         */
        var filename = '';
        var width = params.width ? params.width : 200;
        var height = params.height ? params.height : 200;
        var per_width = params.per_width ? params.per_width : '';
        var outputSize = params.outputSize ? params.outputSize : [0,0];
        var cliparea_height = params.cliparea_height ? params.cliparea_height : '200px';
        var start_func = params.start_func;
        var done_func = params.done_func;
        var complete_func = params.complete_func;

        if(!per_width){
            var per_height = '';
        }else{
            var per_height = params.per_height;
        }
        if(!params.clippanel){console.log('未找到裁剪容器对象');return}
        if(!params.file){console.log('未找到上传文件对象');return}
        if(!params.width && !params.per_width){var width = 200}

        var DOMHTMLSTR = $('<div class="clipArea" style="height: '+ cliparea_height +'"></div><div style="display: none;"></div><p style="margin-top: 3px;"><div style="width: 60px; display: inline-block;" class="button-circle button-circle-small" >确认</div><span style="color: #8d8d8d; margin-left: 5px;">滑动鼠标滚轮调节大小</span></p>');
        DOMHTMLSTR.prependTo(params.clippanel);
        // params.clippanel.append(DOMHTMLSTR);

        var __clipPanelObject = params.clippanel.find('.clipArea');
        var pc = new PhotoClip(__clipPanelObject, {
            size: [width,height],
            outputSize: outputSize,
            adaptive: [""+per_width, ""+per_height],
            file: params.file,
            view: __clipPanelObject.next(),
            ok: __clipPanelObject.next().next().next(),
            loadStart: function() {
                if(start_func){
                    start_func();
                }
            },
            loadComplete: function() {
                params.clippanel.show();
                __clipPanelObject.show();
                __clipPanelObject.next().next().show();
                __clipPanelObject.next().next().next().show();
                __clipPanelObject.next().hide();

                if(complete_func){
                    complete_func();
                }
            },
            done: function(dataURL) {
                var url = '/'+xdock.config.appname+'/resource/tools/file/upload/ajax';
                var formdata = {
                    'image-file': dataURL,
                    'name': params.file.val()
                };
                showloading();
                file_upload(url, formdata, function (data) {
                    done_func(data);
                });
                __clipPanelObject.hide();
                __clipPanelObject.next().next().hide();
                __clipPanelObject.next().next().next().hide();
                __clipPanelObject.next().css('width', __clipPanelObject.children('.photo-clip-layer').css('width'));
                __clipPanelObject.next().css('height', __clipPanelObject.children('.photo-clip-layer').css('height'));
                __clipPanelObject.next().show();
            },
            fail: function(msg) {
                alert(msg);
            },
            style:{
                maskColor: 'rgba(0,0,0,.2)',
            }
        });
    };


    return _xdock;
}

// 文件上传通用函数
function file_upload(url, formData, success, error){
    var _formdata = new FormData();
    var reg = /^data:[a-zA-Z0-9\/]*;base64,/;
    for (var x in formData ){
        // 检测上传的对象是否为base64编码的文件对象
        if(typeof(formData[x])=='string' && formData[x].indexOf('data:')==0 && reg.test(formData[x])){
            _formdata.append(x, convertBase64UrlToBlob(formData[x]));
        }else{
            _formdata.append(x, formData[x]);
        }
    }
    $.ajax({
        url: url,
        data: _formdata,
        type: 'post',
        /**
         *必须false才会自动加上正确的Content-Type
         */
        contentType: false,
        /**
         * 必须false才会避开jQuery对 formdata 的默认处理
         * XMLHttpRequest会对 formdata 进行正确的处理
         */
        processData: false,
        success: function(data){
            success(data);
        },
        error: function(data){
            error(data)
        }
    });
}

// 通用base64url图片转file对象
function convertBase64UrlToBlob(urlData){
    var bytes=window.atob(urlData.split(',')[1]);        //去掉url的头，并转换为byte
    //处理异常,将ascii码小于0的转换为大于0
    var ab = new ArrayBuffer(bytes.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < bytes.length; i++) {
        ia[i] = bytes.charCodeAt(i);
    }
    return new Blob( [ab] , {type : 'image/png'});
};
