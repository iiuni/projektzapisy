from fabric.api import env, run, sudo, local, put

def production():
    """Defines production environment"""
    env.user = "deploy"
    env.hosts = ['example.com',]
    env.base_dir = "/var/www"
    env.app_name = "app"
    env.domain_name = "app.example.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % {'base_dir': env.base_dir, 'domain_name': env.domain_name}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:example/app.git"
    env.git_branch = "master"
    env.max_releases = 3
    # env.env_file = "deploy/production.txt"

def staging():
    """Defines staging environment"""
    env.user = "zapisy"
    env.hosts = ['zapisyuwr.swistak35.com']
    env.base_dir = "/home/zapisy"
    env.app_name = "projektzapisy"
    env.domain_name = "zapisyuwr.swistak35.com"
    env.domain_path = "%(base_dir)s/%(app_name)s" % {'base_dir': env.base_dir, 'app_name': env.app_name}
    env.venv_path = "%(base_dir)s/env27" % {'base_dir': env.base_dir}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:iiuni/projektzapisy.git"
    env.git_branch = "master-dev"
    env.max_releases = 3
    # env.env_file = "deploy/production.txt"

def testing3():
    """Defines staging environment"""
    env.user = "zapisy"
    env.hosts = ['35.165.223.171']
    env.base_dir = "/home/zapisy"
    env.app_name = "projektzapisy"
    env.domain_name = "ec2-35-165-223-171.us-west-2.compute.amazonaws.com"
    env.domain_path = "%(base_dir)s/%(app_name)s" % {'base_dir': env.base_dir, 'app_name': env.app_name}
    env.venv_path = "%(base_dir)s/env27" % {'base_dir': env.base_dir}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:swistak35/projektzapisy.git"
    env.git_branch = "master-dev"
    env.max_releases = 3

def releases():
    """List a releases made"""
    env.releases = sorted(run('ls -x %(releases_path)s' % {'releases_path': env.releases_path}).split())
    if len(env.releases) >= 1:
        env.current_revision = env.releases[-1]
        env.current_release = "%(releases_path)s/%(current_revision)s" % {'releases_path': env.releases_path, 'current_revision': env.current_revision}
    if len(env.releases) > 1:
        env.previous_revision = env.releases[-2]
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % {'releases_path': env.releases_path, 'previous_revision': env.previous_revision}

def start():
    """Start the application servers"""
    run("service zapisy start")

def reload():
    """Reloads your application"""
    run("pkill -HUP -F %(shared_path)s/gunicorn.pid" % {'shared_path': env.shared_path})

def restart():
    """Restarts your application"""
    run("service zapisy restart")

def stop():
    """Stop the application servers"""
    run("service zapisy stop")

def setup():
    """Prepares one or more servers for deployment"""
    run("mkdir -p %(domain_path)s/{releases,shared}" % {'domain_path': env.domain_path})
    run("mkdir -p %(shared_path)s/{logs,system}" % {'shared_path': env.shared_path})

def checkout():
    """Checkout code to the remote servers"""
    from time import time
    env.current_release = "%(releases_path)s/%(time).0f" % {'releases_path': env.releases_path, 'time': time()}
    run("cd %(releases_path)s; git clone -q -o deploy --depth 1 -b %(git_branch)s %(git_clone)s %(current_release)s" % {'releases_path': env.releases_path, 'git_clone': env.git_clone, 'current_release': env.current_release, 'git_branch': env.git_branch})

def update():
    """Copies your project and updates environment and symlink"""
    update_code()
    update_env()
    symlink()
    run("echo \"ALLOWED_HOSTS = %(hosts)s\" >> %(current_release)s/zapisy/settings_local.py" % {'hosts': env.hosts, 'current_release': env.current_release})

def update_code():
    """Copies your project to the remote servers"""
    checkout()

def symlink():
    """Updates the symlink to the most recently deployed version"""
    if not env.has_key('current_release'):
        releases()
    run("ln -nfs %(current_release)s %(current_path)s" % {'current_release': env.current_release, 'current_path': env.current_path})
    run("ln -nfs %(shared_path)s/logs %(current_release)s/zapisy/logs" % {'shared_path': env.shared_path, 'current_release': env.current_release})
    run("ln -nfs %(shared_path)s/system/settings_local.py %(current_release)s/zapisy/settings_local.py" % {'shared_path': env.shared_path, 'current_release': env.current_release})
    run("ln -nfs /home/zapisy/env26/lib/python2.6/site-packages/django/contrib/admin/static/admin %(current_release)s/zapisy/site_media/admin" % {'current_release': env.current_release})

def update_env():
    """Update servers environment on the remote servers"""
    if not env.has_key('current_release'):
        releases()
    run("source %(venv_path)s/bin/activate; pip install -r %(current_release)s/zapisy/requirements.production.txt" % {'current_release': env.current_release, 'venv_path': env.venv_path})

def migrate():
    """Run the migrate task"""
    if not env.has_key('current_release'):
        releases()
    run("source %(venv_path)s/bin/activate; cd %(current_release)s/zapisy; python manage.py migrate" % {'current_release': env.current_release, 'venv_path': env.venv_path})

def cleanup():
    """Clean up old releases"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) > env.max_releases:
        directories = env.releases
        directories.reverse()
        del directories[: env.max_releases]
        env.directories = ' '.join(["%(releases_path)s/%(release)s" % {'releases_path': env.releases_path, 'release': release} for release in directories])
        run("rm -rf %(directories)s" % {'directories': env.directories})

def rollback_code():
    """Rolls back to the previously deployed version"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % {'releases_path': env.releases_path, 'current_revision': env.current_revision}
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % {'releases_path': env.releases_path, 'previous_revision': env.previous_revision}
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % {'current_release': env.current_release, 'previous_release': env.previous_release, 'current_path': env.current_path})

def rollback():
    """Rolls back to a previous version and restarts"""
    rollback_code()
    reload()

def deploy():
    """Deploys your project. This calls both `update' and `restart'"""
    update()
    reload()
