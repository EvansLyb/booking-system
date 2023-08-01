# Booking System Service

## 快速开始
前往 [微信云托管快速开始页面](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/basic/guide.html)，选择相应语言的模板，根据引导完成部署。

## 本地调试
下载代码在本地调试，请参考[微信云托管本地调试指南](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/guide/debug/)

## 实时开发
代码变动时，不需要重新构建和启动容器，即可查看变动后的效果。请参考[微信云托管实时开发指南](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/guide/debug/dev.html)

## 部署发布
代码推送到master(可设置, 详情参考文档)分支时，云托管自动触发流水线。请参考[微信云托管服务管理指南](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/guide/service/pipeline.html#%E6%B5%81%E6%B0%B4%E7%BA%BF)

## Dockerfile最佳实践
请参考[如何提高项目构建效率](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/build/speed.html)


## 目录结构说明
~~~
.
├── Dockerfile                  dockerfile
├── README.md                   README.md文件
├── container.config.json       模板部署「服务设置」初始化配置（二开请忽略）
├── manage.py                   django项目管理文件 与项目进行交互的命令行工具集的入口
├── requirements.txt            依赖包文件
└── core                        放置配置文件及服务网关
    ├── asgi.py                 自动生成文件asgi.py, 异步服务网关接口
    ├── settings.py             项目的总配置文件  里面包含数据库 web应用 日志等各种配置
    ├── urls.py                 URL配置文件  Django项目中所有地址中（页面）都需要我们自己去配置其URL
    └── wsgi.py                 自动生成文件wsgi.py, Web服务网关接口
└── apps                        放置配置文件及服务网关
    └── apis                    api目录, 编写小程序接口逻辑
        ├── migrations          数据移植（迁移）模块
        ├── config.py           配置模块
        ├── models.py           数据模块
        ├── urls.py             路由模块
        └── views.py            执行响应的代码所在模块  代码逻辑处理主要地点  项目大部分代码在此编写
    └── authentication          authentication目录, 编写授权与用户相关逻辑
        ├── management          该目录中文件定义django可执行命令
        ├── migrations          数据移植（迁移）模块
        ├── config.py           配置模块
        ├── forms.py            表单模块
        ├── models.py           数据模块
        ├── urls.py             路由模块
        └── views.py            执行响应的代码所在模块  代码逻辑处理主要地点  项目大部分代码在此编写
    └── dashboard               dashboard目录, 编写后台逻辑
        ├── forms               表单模块目录
        ├── migrations          数据移植（迁移）模块
        ├── templatetags        模版函数目录
        ├── config.py           配置模块
        ├── views               逻辑模块目录
        ├── models.py           数据模块
        ├── urls.py             路由模块
        └── views_ols.py        旧逻辑模块目录, 需迁移至views目录
    ├── static                  静态资源目录
    └── templates               模版目录
~~~


## 使用注意
需要在「服务设置」 - 「基础信息」中补全以下环境变量，才可正常使用，否则会引发无法连接数据库，进而导致部署失败。
- DB_ENGINE
- MYSQL_DATABASE
- MYSQL_USERNAME
- MYSQL_PASSWORD
- MYSQL_ADDRESS
此项目使用云托管内MySQL，可以在控制台MySQL页面获取相关信息。
