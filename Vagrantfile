# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.ssh.shell = "bash"
  config.vm.box = "ubuntu/bionic64"
  config.vm.box_url = "https://app.vagrantup.com/ubuntu/boxes/bionic64"
  config.vm.provision :shell, path: "env/apt.sh"
  config.vm.provision :shell, path: "env/apache_setup.sh"
  config.vm.provision :shell, path: "env/postgre_setup.sh"
  config.vm.provision :shell, path: "env/tools_install.sh"
  config.vm.provision :shell, path: "env/nodejs_setup.sh"
  config.vm.provision :shell, path: "env/py3.sh"
  config.vm.provision :shell, path: "env/webpack_setup.sh", privileged: false
  config.vm.provision :shell, path: "env/bash_setup.sh", privileged: false
  config.vm.provision :shell, path: "env/redis.sh"
  config.vm.provision :shell, path: "env/env3_setup.sh", privileged: false
  config.vm.network :forwarded_port, guest: 80, host: 8001
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 5432, host: 15432

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    # The folder "node_modules" will live somewhere else and only be mounted
    # in /vagrant/zapisy to avoid the issue with symlinks on Windows.
    config.vm.provision "shell", inline: <<-SHELL
      echo "Preparing local node_modules folder…"
      mkdir -p /vagrant_node_modules
      chown vagrant:vagrant /vagrant_node_modules
    SHELL
    config.vm.provision "shell", run: "always", inline: <<-SHELL
      mkdir -p /vagrant/zapisy/node_modules
      mount --bind /vagrant_node_modules /vagrant/zapisy/node_modules
    SHELL
  end
end
