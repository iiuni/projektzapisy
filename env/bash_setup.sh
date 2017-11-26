echo "alias prepare-env='source /home/vagrant/env2.6/bin/activate'" >> .bash_aliases
echo "alias prepare-env27='source /home/vagrant/env2.7/bin/activate'" >> .bash_aliases
echo "alias get-settings='cp /vagrant/env/settings_local.py /vagrant/zapisy/zapisy'" >> .bash_aliases
echo "alias reset-database='sudo su - postgres -c \"psql -f reset_zapisy.sql\"'" >> .bash_aliases
echo "alias load-database='sudo su - postgres -c \"psql -f /vagrant/a_dump_20160301.sql fereol\"'" >> .bash_aliases
echo "alias runserver='python manage.py runserver 0.0.0.0:8000'" >> .bash_aliases
echo "alias migrate='python manage.py makemigrations && python manage.py migrate'" >> .bash_aliases
echo "alias development-setup='mkdir /vagrant/zapisy/logs && get-settings && sudo su - postgres -c \"psql -f /vagrant/db_dump.sql fereol\" && cd /vagrant/zapisy && migrate'" >> .bash_aliases
echo "source /home/vagrant/env2.7/bin/activate" >> .bashrc
