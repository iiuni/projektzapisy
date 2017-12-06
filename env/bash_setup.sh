echo "alias prepare-env27='source ~/env2.7/bin/activate'" >> .bash_aliases
echo "alias prepare-env35='source ~/env3/bin/activate'" >> .bash_aliases
echo "alias get-settings='cp /vagrant/env/settings_local.py .'" >> .bash_aliases
echo "alias reset-database='sudo su - postgres -c \"psql -f reset_zapisy.sql\"'" >> .bash_aliases
echo "alias load-database='sudo su - postgres -c \"psql -f /vagrant/a_dump_20160301.sql fereol\"'" >> .bash_aliases
echo "alias runserver='python manage.py runserver 0.0.0.0:8000'" >> .bash_aliases
echo "source ~/env3/bin/activate" >> .bashrc
