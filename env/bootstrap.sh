#!/usr/bin/env bash

##########################################################
#  install apache  #######################################
apt-get update
apt-get install -y apache2
if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi
apt-get install -y apache2-dev
#  end install apache/////////////////////////////////////
##########################################################


##########################################################
#  install postresql######################################
##########################################################
APP_DB_USER=fereol
APP_DB_PASS=fereolpass
APP_DB_NAME=fereol
PG_VERSION=9.5
#---------------------------------------------------------

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

# Update package list and upgrade all packages
apt-get update
apt-get -y upgrade

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
#  end install postgresql/////////////////////////////////
##########################################################

# get tools and dev libs

apt-get -y install git
apt-get -y install python2.7 python-dev python-pip python-virtualenv
apt-get -y install libpq-dev
apt-get -y install unzip
apt-get -y install libxml2-dev libxslt1-dev
apt-get -y install build-essential
apt-get -y install libncursesw5-dev libncurses5-dev
apt-get -y install libreadline5-dev
apt-get -y install libssl-dev
apt-get -y install libgdbm-dev
apt-get -y install libbz2-dev
apt-get -y install libc6-dev
apt-get -y install libsqlite3-dev
apt-get -y install tk-dev
apt-get -y install libjpeg62-dev
apt-get -y install libfreetype6-dev
apt-get -y install liblcms1-dev
apt-get -y install xvfb
apt-get -y install firefox
apt-get -y install memcached

# install firefox45 and geckodriver for selenium
# firefox45
wget https://ftp.mozilla.org/pub/firefox/releases/45.0/linux-x86_64/en-US/firefox-45.0.tar.bz2
tar -xjf firefox-45.0.tar.bz2
sudo rm -rf  /opt/firefox
sudo mv firefox /opt/firefox45
sudo mv /usr/bin/firefox /usr/bin/firefoxold
sudo ln -s /opt/firefox45/firefox /usr/bin/firefox
# geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.13.0/geckodriver-v0.13.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/

# download and hack broken zlib
apt-get -y install zlib1g-dev
# cd /lib
# ln -s x86_64-linux-gnu/libz.so.1 libz.so

# Install redis
apt-get -y install redis-server

# For good measure
pip install --upgrade pip
pip install --upgrade virtualenv

# Grab Python 3.6
add-apt-repository -y ppa:jonathonf/python-3.6
apt-get -y update
apt-get -y install python3.6
