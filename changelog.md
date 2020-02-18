模块升级日志
---

#### 2017-12-10 @孙海峰

```
    描述：FALY欢迎标语修改为：FALY，精致生活
    升级备忘：
        修改配置文件：config.dev.yaml、config.pro.yaml
        appname_cn_long："FALY"
        slogan: "FALY，精致生活。"
```

#### 2017-11-29 @孙海峰
```
    描述：FALY专家初步实现
    升级备忘：
        1、app_faly_server、app_falyconsole_server、xdock_faly_server升级至最新
        2、新增表 faly_expert、faly_expert_college_topic、faly_expert_activity、faly_expert_news、
            faly_expert_plan、faly_expert_project
```

#### 2017-11-16 @孙海峰
```
    描述：
        1、学院第一版;
        2、推荐文章模型增加封面字段;
    升级备忘：
        1.app_falyconsole_server、xdock_edu_server、xdock_order_server模块升级至最新；
        2.各模块下的yaml配置文件中增添新项【测试环境 与 正式环境分别对应】：
            rds:
                binds:
                    edu: ......
        3.创建数据库表：
            edu_college_category、edu_college_topic、edu_college_lesson、edu_college_lesson_item
        4.修改  order_mall2_sku 表结构：
            alter table order_mall2_sku ADD COLUMN product TEXT NULL ;
        5、修改 faly_prefer_article 表结构：
            alter table faly_prefer_article add COLUMN cover VARCHAR(2048) NULL;
```


#### 2017-11-03 @孙海峰
```
    描述：食谱重构
    升级备忘：
        1、app_faly_server、app_falyconsole_server、xdock_faly_server升级至最新；
        2、新增表:
            faly_new_recipes、faly_new_recipes_category、faly_new_recipes_food、
            faly_new_recipes_plan、faly_new_recipes_plan_daily、faly_new_recipes_user_plan；
        3、执行app_faly_server的tools/migration下的  from_recipes_to_newrecipes.py  文件，进行数据迁移
```

#### 2017-10-20 @sunhaifeng 
```
    描述： 项目-计划功能实现
    升级备忘：
        新增如下表：
            faly_pp_category、faly_pp_plan、faly_pp_plan_time、faly_pp_project、faly_pp_userplan、faly_pp_userplan_time
```

#### 2017-10-17 @sunhaifeng
```
    描述：
        1、FALY余额日报去除冻结金额；
        2、调整权限路由
    升级备忘：
        1、该模块直接升级；
        2、控制台设置余额日报权限
```

#### 2017-09-30 @tengfei
```
    商品分类添加封面
    升级备忘:
    1. 升级 xdock_order
```

#### 2017-09-11 @tengfei
```
    描述: FALY商城添加 商城2.0 和 积分商城
    升级备忘:
    1. 升级 xdock_order, xdock_faly, app_faly
```


#### 2017-09-27 @sunhaifeng

```
    描述： 增添用户自定义绑定团队功能
    升级备忘：
        创建表 user_staff_team
```

#### 2017-09-08 @sunhaifeng

```
    描述：平台增添推送文章功能
    升级备忘：
        1、创建表： faly_prefer_article
```

#### 2017-08-28 @sunhaifeng

```
    描述：FALY收益账户第一版
    升级备忘：
        1、创建表：faly_revenue_balance、faly_revenue_balance_bill、 faly_revenue_balance_withdraw;
        2、平台消息管理添加消息：
             revenue.balance.offline_consume（收益账户线下扣款）、
             revenue.balance.recharge（收益账户充值）
```

#### 2017-08-21 @tengfei

```
    描述: 平台运营添加用户消息模板管理
```

#### 2017-08-15 @孙海峰

```
    描述：
        1.FALY控制台权限控制
        2.形体日记/记录点击发送后，给用户发送微信及短信消息
        3.形体日记不再使用富文本框编辑日记简介
        4.形体日记记录，在所属日记主体不发送的情况下，不给予发送权限
    升级备忘：
        1.user_staff_role表增添新数据：
            INSERT INTO user_staff_role(roleid, roleno, name, abstract, status, ut, ct, permission_urls) VALUES ('dab2edf080ca11e7bd34a0c589188e1d', '999', '默认权限', '普通用户默认权限控制', 'normal', '2017-08-14 16:31:46', '2017-08-14 16:30:40', ’');
        2.修改配置文件：
            (1).chuanglan_sms_template项下增添:
                127: ......
            (2).usermessage_sms_mustsend项下增添:
                - faly.charmlog*
            (3).template_message_ids项下增添:
                faly.charmlog: ......
```

#### 2017-08-07 @孙海峰

```
    描述： FALY形体日记管理
    升级备忘：
        创建表charm_log、charm_log_record
```

#### 2017-07-31 @孙海峰

```
    描述：
        客户关联/解绑团队时，通知到团队的每个成员
    升级备忘：
        修改配置文件：
            chuanglan_sms_template：修改项目为：
                126: 【FALY集团】您好，%s%s%s。FALY，让您发现更好的自己！
```

#### 2017-07-24 发布 @fachang


#### 2017-07-24 @fachang

```
	1. 实现sku短视频配置，定时上架下架配置，原价配置，销售基数配置
```


#### 2017-07-24 @孙海峰

```
    描述：
        1. 用户关联/解绑专属团队给予微信/短信提醒
        2.增添用户团队是否为主团队功能。
        3.FALY亚健康报告增加签字及专属团队印章等优化
    升级备忘：
        1.修改app_faly、app_falyconsole配置文件
            chuanglan_sms_template：新增项目：
                126: 【FALY集团】您好，您%s%s。FALY，让您发现更好的自己！
            usermessage_sms_mustsend：新增项目：
                - faly.user.serviceteam*
            template_message_ids：新增项目：
                faly.user.serviceteam: tifkJO8p4JngDov4ZfCl-r1R9JVYKEoiGvWjWp8l6jU
            生产环境：
                faly.user.serviceteam: peN8gP2c_JjHem1CjaFDK2j_ACLUGETlAPVo0qhr_yk
        2.修改数据库表 user_serviceteam_own ：
            ALTER TABLE user_serviceteam_own ADD COLUMN ismain VARCHAR(32) NULL
        
        3.修改表结构：
            alter table faly_log add column counselora varchar(32) null;
            alter table faly_log add column counselorb varchar(32) null;
            alter table faly_log add column counselorc varchar(32) null;
            alter table faly_log add column counselord varchar(32) null;
            alter table faly_log add column checkstatus varchar(32) null DEFAULT 'unchecked';
        4.修改历史数据：
            UPDATE faly_log SET checkstatus = 'checked';
            
```
    
#### 2017-07-18 @孙海峰
```
    描述：FALY体质分析报告修改
    升级备忘：
        1.修改数据库表faly_log_template:
            # alter table faly_log_template add column header varchar(32) null default '0';
            # alter table faly_log_template add column suggestion text null;
            # alter table faly_log_template add column teamid varchar(32);
            # alter table faly_log_template add column classes varchar(32) null;
            # alter table faly_log_template add column checkstatus varchar(32) null DEFAULT 'checked';
        2.修改数据库表faly_log：
            # alter table faly_log add column header varchar(32) null default '0';
            # alter table faly_log add column suggestion text null;
            # alter table faly_log add column teamid varchar(32);
            # alter table faly_log add column reportno varchar(32) null default '0';
            # alter table faly_log add column healthindex varchar(32) null;
            # alter table faly_log add column classes varchar(32) null;
```

#### 2017-07-14 @孙海峰
```
    描述：预约短信及微信模板调整
    升级备忘：
        1、删除chuanglan_sms_template项下的 key 为124的子项 ；
        2、chuanglan_sms_template新增124、125短信模板子项；
        3、生产环境配置文件的template_message_ids下的faly.appointment.apply子项
```

#### 2017-07-12 @孙海峰
```
    描述：用户级别修改发送微信消息，修改健康管理->专属服务；FALY环球医城->FALY商城；
    升级备忘：
        1.修改配置文件:
            (1)、chuanglan_sms_template项下的短信签名全部修改为FALY集团；
            (2)、chuanglan_sms_template新增子项：
                chuanglan_sms_template：
                    ...
                    124: 【FALY集团】%s
        2.生产环境微信公众平台的模板消息中添加编号为：OPENTEAM401226262 的模板
                    
```

#### 2017-07-07 @孙海峰
```
    描述：新增用户关系管理CRM
    升级备忘：
        1.新增xdock_crm模块
        2.创建表 crm_marketrecord
        3.修改配置文件main:rds:binds项目：
            main:
                ...
                rds:
                    ...
                    binds:
                        ...
                        crm: mysql+pymysql://buddytest:12345qwertrds@123.56.66.31:3306/faly?charset=utf8mb4
        
        
```

#### 2017-06-28 @孙海峰
```
    描述：新增预约管理，微信、短信、企业号通知
    升级备忘：
        1.修改配置文件
            (1).chuanglan_sms_template项下新增子项:
                    chuanglan_sms_template
                        ...
                        123: 【FALY健康集团】%s
            (2).usermessage_sms_mustsend项下新增子项:
                    usermessage_sms_mustsend:
                        ...
                        - faly.appointment.apply*
            (3).template_message_ids项下新增子项:
                    template_message_ids:
                        ...
                        faly.appointment.apply: d11f5vx8JHuErrOIFjzzSaLTMzNzRY94N7xX-oLyoak
```

#### 2017-06-26 @孙海峰
```
    描述：预约申请管理功能
    升级备忘：
        1.创建表 faly_appointment_apply
```

#### 2017-06-21 @孙海峰
```
    描述：职工管理添加机构、机构成员管理功能、健康管理报告选择部位改为分类
    升级备忘：
        1.创建表faly_organization_staff
        2.修改faly_organization表结构：
            alter table faly_organization drop COLUMN username
        3.修改配置文件中的outreport_parts为：
            outreport_parts: ['报告单(请于正常光线下拍摄上传)', 'X光/CT/MR(请将片子背对光源拍摄)']
```

#### 2017-06-19 @孙海峰
```
    描述：机构管理功能发布及职工管理添加所属机构
    升级备忘：
        1.创建表　faly_organization；

```

#### 2017-06-14 @孙海峰
```
    描述：增添用户专属服务团队logo和详情
    升级备忘：
    1.修改数据库user_serviceteam表结构
        alter table user_serviceteam add column logourl text null;
        alter table user_serviceteam add column detail text null;
    2.重命名user_team 为 user_serviceteam_own
        rename table user_team to user_serviceteam_own;

```

#### 2017-06-13 @孙海峰
```
    描述：新版本用户专属服务团队功能整改
    升级备忘：
    1.创建数据库表
        user_team
    2.修改数据库表user_serviceteam表结构
        alter table user_serviceteam drop column uid;
        alter table user_serviceteam drop column username;

```

#### 2017-06-05 @孙海峰

```
    描述：实现FALY用户专属服务团队管理功能
    升级备忘：
    1.修改配置文件：
        删除配置文件中的user段下的userteamroles项

```

#### 2017-06-05 @孙海峰

```
    描述：实现FALY用户专属服务团队管理功能
    升级备忘：
    1.创建数据库表：
        user_serviceteam，user_serviceteam_role，user_serviceteam_member

```

#### 2017-05-24 @孙海峰

```
    描述：实现FALY用户资料管理功能
    升级备忘：
    1.创建数据库表：
        faly_out_report， faly_report_image
    2.修改配置文件
        新增 faly 段，并在该段下新增 healthage 段，然后继续新增 outreport_parts 段
        如：
            faly:
              healthage:
                outreport_parts: []

```
#### 2017-05-19 @李法昌

```
    举例说明更新日志需要写明哪些内容，目的是让使用者可以顺利完成模块升级。

	升级备忘：
	1. 修改user表
	   alter table user add column levelid varchar(32);
	   alter table user add index level_index (levelid);
	2. 修改配置文件
	   配置文件user段下增加xxxx，比如：xxxx
	3. 需要进行数据迁移
	   需要将表yyy字段数据迁移到表zzz字段。

	类似这种格式，让使用者一目了然。避免经常性的低级遗忘导致的升级失败。


```
