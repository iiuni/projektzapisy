# set up virtualenv
cd $HOME
python3.6 -m venv env3
source env3/bin/activate

# The version of python we've built won't necessarily
# have the latest version of pip bundled with it
pip install --upgrade pip

# get requirements
pip install -r /vagrant/zapisy/requirements.development.txt

echo "Python 3.6 environment has been set up."
