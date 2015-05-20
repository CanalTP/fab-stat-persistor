import os
from fabric.api import env, run
from fabtools.files import upload_template

def _upload_template(filename, destination, context=None, chown=True, user='www-data', **kwargs):
    kwargs['use_jinja'] = True
    kwargs['template_dir'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          os.path.pardir, 'templates')
    kwargs['context'] = context
    kwargs['mkdir'] = False
    kwargs['chown'] = chown
    kwargs['user'] = user
    kwargs['use_sudo'] = True
    kwargs['backup'] = False
    upload_template(filename, destination, **kwargs)


def get_psql_version():
    version_lines = run('psql --version')
    v_line = version_lines.split('\n')[0]
    return v_line.split(" ")[-1].split(".")

