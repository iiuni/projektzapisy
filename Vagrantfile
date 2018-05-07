# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_url = "https://app.vagrantup.com/ubuntu/boxes/xenial64"
  config.vm.provision :shell, path: "env/bootstrap.sh"
  config.vm.provision :shell, path: "env/setup_npm.sh", privileged: false
  config.vm.provision :shell, path: "env/bash_setup.sh", privileged: false
  config.vm.provision :shell, path: "env/env3_setup.sh", privileged: false
  config.vm.network :forwarded_port, guest: 80, host: 8001
  config.vm.network :forwarded_port, guest: 8000, host: 8002
  config.vm.network :forwarded_port, guest: 5432, host: 15432

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
  end
end
