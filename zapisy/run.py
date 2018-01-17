import os

import click
from fabric.api import env
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
def server(ip, port):
    """
    Run development server
    """
    cmd = 'runserver {ip}:{port}'.format(ip=ip, port=port)
    run_locally_with_manage_py(cmd)


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


@click.option("--path", default='')
@click.option("--user", default='fereol')
@click.command()
def load(path, user):
    """
    Load database
    """
    local('sudo su - postgres -c \"psql -f {db_path} {db_user}\"'.format(
        db_path=path, db_user=user))


@click.command()
def reset():
    """
    Reset default database
    """
    local('sudo su - postgres -c \"psql -f reset_zapisy.sql\"')

db.add_command(load)
db.add_command(reset)


cli.add_command(dc)
cli.add_command(tests)
cli.add_command(server)
cli.add_command(db)

if __name__ == '__main__':
    cli()
