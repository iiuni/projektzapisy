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
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "infra/playbooks/dev/playbook.yml"
  end
  config.vm.network :forwarded_port, guest: 80, host: 8001
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 5432, host: 15432

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
    vb.cpus = "2"
    # Enable "IO APIC" for better multicore performance, see
    # https://serverfault.com/questions/74672/why-should-i-enable-io-apic-in-virtualbox
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
end
