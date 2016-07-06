from fabric.api import env
from fabric.decorators import task
import os
from importlib import import_module

env.repo = 'git@github.com:CanalTP/navitia-stat-persistor.git'
env.branch = 'master'

env.USER = 'www-data'

env.release_to_keep = 5

#postgis dir is usefull for old postgis version where we cannot  do a 'create extention'
env.postgis_dir = '/usr/share/postgresql/9.1/contrib/postgis-1.5'

env.rabbitmq_host = 'localhost'
env.rabbitmq_port = 5672

env.broker_exchange = 'stat_persistor_exchange_topic'

env.broker_username = 'guest'
env.broker_password = 'guest'

env.broker_queue = 'stat_persistor_queue'

env.postgresql_user = 'navitia_stat'
env.postgresql_password = 'navitia_stat'
env.postgresql_database = 'statistics'
env.postgresql_database_host = 'localhost'
env.postgresql_port = 5432


env.log_dir = '/var/log/stat_persistor/'
env.deploy_to = '/srv/stat_persistor'
env.log_file = os.path.join(env.log_dir, 'stat_persistor.log')

env.settings_file = os.path.join(env.deploy_to, 'current/stat_persistor.json')
env.alembic_file = os.path.join(env.deploy_to, 'current/migrations/alembic.ini')

@task
def let(**kwargs):
    """
    This function is a way to give env variables in the cli

    call then

    fab dev let:x=bob,z=toto upgrade_all

    to have a env.x and env.z variable
    """
    env.update(kwargs)


""" Environnements """

@task
def use(module_path, *args):
    pos = module_path.rfind(".")
    if pos == -1:
        path, f_name = module_path, module_path
    else:
        path, f_name = module_path[:pos], module_path[pos+1:]
    module = import_module(path)
    getattr(module, f_name)(*args)
