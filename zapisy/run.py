import os
import subprocess
import sys

import click
from fabric.operations import local


@click.group()
def cli():
    """
    Unified way to run things
    """
    pass


def run_locally_with_manage_py(cmd):
    local('python manage.py {cmd}'.format(cmd=cmd))


@click.command()
@click.argument('cmd', required=True)
def dc(cmd):
    """
    Run django command
    """
    run_locally_with_manage_py(cmd)


# Some most used commands have their own names
@click.command()
@click.option('--ip', default='0.0.0.0')
@click.option('--port', default=8000)
@click.option('--no-package-install', '-n', is_flag=True, default=False)
def server(ip, port, no_package_install):
    """
    Run development server.
    Install all required node dependencies before.
    """

    if no_package_install:
        print("******************************************")
        print("WARNING: Skipping Node/Webpack packages installation. " +
              "Only use this option if you know what you're doing.")
        print("******************************************")
    else:
        npm_result = os.system("yarn")
        npm_exit_code = os.WEXITSTATUS(npm_result)
        if npm_exit_code != 0:
            click.echo(click.style("Package installation failed with exit code {}".format(
                npm_exit_code), fg='red'))
            sys.exit(1)

    p1 = subprocess.Popen([
        "python", "manage.py", "runserver", "{ip}:{port}".format(
            ip=ip, port=port)])
    p2 = subprocess.Popen(["yarn", "devw"])
    p3 = subprocess.Popen(["python", "manage.py", "rqworker", "default"])
    p4 = subprocess.Popen(["python", "manage.py", "rqworker", "dispatch-notifications"])

    p1.wait()
    p2.wait()
    p3.wait()
    p4.wait()
    sys.exit(0)


@click.command()
@click.argument("app", default="")
@click.option(
    "--frontend", default=False, help='run selenium tests', is_flag=True)
def tests(app, frontend):
    """
    Run tests
    """
    if frontend:
        local('xvfb-run python manage.py test test_app --nomigrations')
    else:
        run_locally_with_manage_py(
            'test {app} --nomigrations'.format(app=app))


@click.group()
def db():
    """
    Database related commands
    """
    pass


@click.argument("path", required=True)
@click.option("--user", default='fereol')
@click.command()
def load(path, user):
    """
    Load database
    """
    # remove old db
    local('sudo su - postgres  <<\'ENDSUDO\'\n'
          'psql -c "DROP DATABASE \"fereol\";"\n'
          'psql -c "CREATE DATABASE \"fereol\";"\n'
          'logout\n'
          'ENDSUDO\n')

    # new db
    local('PGPASSWORD="fereolpass" psql -U fereol -h localhost -f {db_path} {db_user}'.format(
          db_path=path, db_user=user))


db.add_command(load)


cli.add_command(dc)
cli.add_command(tests)
cli.add_command(server)
cli.add_command(db)

if __name__ == '__main__':
    cli()
