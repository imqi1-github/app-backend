# 实现了数字计数器的后端脚手架

本项目使用 Flask 处理网络请求，使用 SQLAlchemy 处理数据库相关操作，使用 Alembic 迁移数据库。

**安装相关依赖：**

```shell
pip install -r requirements.txt
```

启动服务器：

```shell
python -m main
# 或
python -m core.app
# 或
sh start.sh
```

项目结构：

```
backend
│
├── alembic/    用于数据库迁移
├── blueprints/ 路由相关
├── core/       运行项目相关
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   └── db.py
│
├── static/     静态文件相关
├── templates/  模板文件相关
│
├── config.yaml 数据库配置文件
├── migrate.sh  数据库迁移脚本
├── requirements.txt
├── run.py
└── .gitignore
```

需要扩展路由就在 blueprints 文件夹新建 Python 文件，然后模仿 number.py 那样写，然后在 blueprints.\_\_init\_\_ 文件中或 core.app 加入此蓝图。

需要修改数据库模型就在 core/db.py 中修改，然后执行数据库迁移脚本。

执行数据库迁移脚本就运行 migrate.sh 脚本。