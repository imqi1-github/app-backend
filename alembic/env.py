from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from core.db import db_url, BaseModel  # 导入你定义的 get_db_url 方法

# 这里是 Alembic 配置对象，提供对正在使用的 .ini 配置文件的访问
config = context.config

# 解释配置文件用于 Python 日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置模型的 MetaData
target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移"""
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移"""
    connectable = engine_from_config({'sqlalchemy.url': db_url}, prefix="sqlalchemy.", poolclass=pool.NullPool, )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# 根据是否处于离线模式来选择执行方式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
