# set up virtualenv
cd $HOME
virtualenv -p python3.6 env3
source env3/bin/activate

# get requirements
pip install -r /vagrant/zapisy/requirements.development.txt

echo "Python 3.6 environment has been set up."
