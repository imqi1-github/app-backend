# 实现了数字计数器的后端脚手架

本项目使用 Flask 处理网络请求，使用 SQLAlchemy 处理数据库相关操作，使用 Alembic 迁移数据库。

**安装相关依赖：**

```shell
pip install -r requirements.txt
```

启动服务器：

```shell
python -m main
```

项目结构：

```
backend
│
├── migrations/         用于数据库迁移
├── app/                运行项目相关
│   ├── blueprints/     蓝图
│   ├── models/         数据模型
│   ├── __init__.py     应用对象
│   ├── exteinsions.py  应用扩展，包含SQLAlchemy和数据库迁移工具     
│   └── config.py       读取配置
│
├── static/     静态文件相关
├── templates/  模板文件相关
│
├── config.yaml 数据库配置文件
├── migrate.sh  数据库迁移脚本
├── requirements.txt
├── main.py     项目入口
└── .gitignore
```

需要扩展路由就在 blueprints 文件夹新建 Python 文件，然后模仿 number.py 那样写，然后在 blueprints.\_\_init\_\_ 文件中或 app 加入此蓝图。

需要修改数据库模型就在 models 中修改，然后执行数据库迁移脚本。

执行数据库迁移脚本就运行 migrate.sh 脚本。

若要部署至生产环境中，请指定环境变量 `ENVIRONMENT=production`，然后更新 config.yaml 中 production 分支的配置。