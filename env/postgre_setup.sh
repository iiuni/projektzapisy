#!/usr/bin/env bash

APP_DB_USER=fereol
APP_DB_PASS=fereolpass
APP_DB_NAME=fereol
PG_VERSION=9.5

print_db_usage () {
  echo "Your PostgreSQL database has been setup and can be accessed on your local machine on the forwarded port (default: 15432)"
  echo "  Host: localhost"
  echo "  Port: 15432"
  echo "  Database: $APP_DB_NAME"
  echo "  Username: $APP_DB_USER"
  echo "  Password: $APP_DB_PASS"
  echo ""
  echo "Admin access to postgres user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo ""
  echo "psql access to app database user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost $APP_DB_NAME"
  echo ""
  echo "Env variable for application development:"
  echo "  DATABASE_URL=postgresql://$APP_DB_USER:$APP_DB_PASS@localhost:15432/$APP_DB_NAME"
  echo ""
  echo "Local command to access the database via psql:"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost -p 15432 $APP_DB_NAME"
}

export DEBIAN_FRONTEND=noninteractive

PROVISIONED_ON=/etc/vm_provision_on_timestamp
if [ -f "$PROVISIONED_ON" ]
then
  echo "VM was already provisioned at: $(cat $PROVISIONED_ON)"
  echo "To run system updates manually login via 'vagrant ssh' and run 'apt-get update && apt-get upgrade'"
  echo ""
  print_db_usage
  exit
fi

PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list
if [ ! -f "$PG_REPO_APT_SOURCE" ]
then
  # Add PG apt repo:
  echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" > "$PG_REPO_APT_SOURCE"

  # Add PGDG repo key:
  wget --quiet -O - https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -
fi


# get Polish locale
locale-gen pl_PL.UTF-8
update-locale

apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION"

PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Edit postgresql.conf to change listen address to '*':
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

# Restart so that all new config is loaded:
service postgresql restart

# Create sql for recreating database
cat << EOF > /var/lib/postgresql/reset_zapisy.sql
DROP DATABASE $APP_DB_NAME;
DROP DATABASE test_$APP_DB_NAME;

CREATE DATABASE $APP_DB_NAME WITH OWNER=$APP_DB_USER
                                  LC_COLLATE='pl_PL.UTF-8'
                                  LC_CTYPE='pl_PL.UTF-8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;

CREATE DATABASE test_$APP_DB_NAME WITH OWNER=$APP_DB_USER
                                  LC_COLLATE='pl_PL.UTF-8'
                                  LC_CTYPE='pl_PL.UTF-8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;

EOF

# Create database
cat << EOF | su - postgres -c psql
-- Create the database user:
CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASS';

-- Create the database:
CREATE DATABASE $APP_DB_NAME WITH OWNER=$APP_DB_USER
                                  LC_COLLATE='pl_PL.UTF-8'
                                  LC_CTYPE='pl_PL.UTF-8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;

-- Create the database:
CREATE DATABASE test_$APP_DB_NAME WITH OWNER=$APP_DB_USER
                                  LC_COLLATE='pl_PL.UTF-8'
                                  LC_CTYPE='pl_PL.UTF-8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;

ALTER USER $APP_DB_USER CREATEDB;

EOF

echo "Successfully created PostgreSQL dev virtual machine."
echo ""
print_db_usage
