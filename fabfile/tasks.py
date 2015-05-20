from fabric.colors import blue, red, yellow, green
from fabric.context_managers import warn_only, cd
from fabric.api import run, env, task, execute, roles, local, lcd, runs_once
from fabric.operations import put
from fabfile import utils
from fabfile.component import db
from fabric.contrib.files import exists
from time import sleep
from fabtools import service, require, deb, files
import os, datetime

@task
def deploy():
    """
    deploy stat persistor on the selected platform
    """
    execute(init)
    tar = build_tar(env.repo, env.branch)
    execute(create_release)
    execute(upload_source, tar)
    execute(update_dependancy)
    execute(update_current)
    execute(stop_stat_persistor)
    execute(upload_config)
    execute(upgrade_db)
    execute(start_stat_persistor)
    sleep(5)
    execute(stat_persistor_status)
    print green('removing old releases')
    execute(purge_release)

@task
def init():
    execute(init_app)
    execute(init_db)

@task
@roles('app')
def init_app():
    require.files.directories([env.deploy_to, '{}/releases'.format(env.deploy_to), env.log_dir], owner=env.USER)
    require.deb.packages([
        'unzip',
        'python2.7',
        ])
    utils._upload_template('stat_persistor.jinja', '/etc/init.d/stat_persistor', mode='755',
                     context={
                        'env': env
                     })

@task
@roles('db')
def init_db():
    require.postgres.server()
    require.deb.packages([
        'postgis',
        'postgresql-9.1-postgis',
        'sudo',
    ])
    require.postgres.user(env.postgresql_user, env.postgresql_password)
    require.postgres.database(env.postgresql_database, owner=env.postgresql_user, locale='en_US.UTF-8')
    db.postgis_initdb(env.postgresql_database)

def build_tar(repo, branch):
    if not os.path.isdir('repo'):
        local('git clone {} repo'.format(repo))
    else:
        with lcd('repo'):
            local('git fetch origin')

    output = os.path.abspath('source.tar.gz')
    with lcd('repo'):
        local('git checkout {branch}'.format(branch=branch))
        local('git rebase')
        local('git submodule update --init')
        local("""{{ git ls-files; git submodule foreach --recursive --quiet 'git ls-files --with-tree="$sha1" |sed "s#^#$path/#"'; }} |sed "s#^##" |xargs tar -c -C. -f "{output}" --""".format(output=output))
    return output

@task
@roles('app')
def create_release():
    env.release = '{}/releases/{}'.format(env.deploy_to, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    require.files.directory(env.release, owner=env.USER)

@task
@roles('app')
def upload_source(tar):
    with cd(env.release):
        put(tar, 'source.tar.gz')
        run('tar xf source.tar.gz')

@task
@roles('app')
def update_dependancy():
    with cd(env.release):
        run('pip install -r requirements.txt')
        run('python setup.py build_pbf')

@task
@roles('app')
def purge_release():
    with cd('{}/releases'.format(env.deploy_to)):
        run('(ls -t|head -n {};ls)|sort|uniq -u|xargs rm -rf'.format(env.release_to_keep))

@task
@roles('app')
def update_current():
    with cd(env.deploy_to):
        if exists('current'):
            run('rm current')
        run('ln -s {} current'.format(env.release))

@task
@runs_once
@roles('app')
def upgrade_db():
    with cd('{}/current/migrations'.format(env.deploy_to)):
        run('PYTHONPATH=. alembic upgrade head')


@task
@roles('app')
def upload_config():
    utils._upload_template("stat_persistor.json.jinja", env.settings_file,
                     context={
                        'env': env
                     })

    utils._upload_template('alembic.ini.jinja', env.alembic_file,
                     context={
                         'env': env
                     })

@task
@roles('app')
def stop_stat_persistor():
    with warn_only():
        require.service.stopped("stat_persistor")

@task
@roles('app')
def start_stat_persistor():
    require.service.started("stat_persistor")

@task
@roles('app')
def stat_persistor_status():
    if exists("/etc/init.d/stat_persistor"):
        run("service stat_persistor status")
    else:
        print(yellow("WARNING: /etc/init.d/stat_persistor does not exists."))

@task
@roles('app')
def remove_old_install():
    """
    remove old packages from navitia
    """
    if deb.is_installed('navitia-stat-persistor'):
        execute(stop_stat_persistor)
        deb.uninstall('navitia-stat-persistor', purge=True)
        files.remove('/srv/stat_persistor/alembic.ini')
        files.remove('/srv/stat_persistor/stat_persistor.json')
    else:
        print yellow('No old installation detected')
