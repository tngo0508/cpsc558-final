

# CPSC 558 - Final Project

Our final project repo. Woot.

* Mike Peralta mikeperalta@csu.fullerton.edu
* Thomas Ngo tngo0508@csu.fullerton.edu
* Andy Nguyen andy21996@csu.fullerton.edu

## Professor Instructions

First, you can use the command ```make``` in the root of this repo for a list of commands that GNU Make will help you run.

You will use your host machine to control your VM.
All changes will be made to the remote VM,
and all changes will be run there as well.
No changes or tests will be performed on your host machine.

Essentially, you'd need to go through the following steps:

1. Setup a fresh Ubuntu 16.04 VM (Sorry !!!). You probably want to assign it multiple cores so our test server/clients don't choke and hide the benefits of using a switch over a hub, too much.

2. Make sure the VM can reach the internet, and is reachable by your host machine (we used bridged mode)

3. Setup the root account's password or SSH key so the user on your current machine can SSH into the VM using the root user

4. Set the environment variable UBUNTU_VM_HOST to the IP address or hostname of your Ubuntu 16 VM
    (you'll see Make mention the value it's reading), with something like:
    
    ```export UBUNTU_VM_HOST=192.168.1.x```
    
    (where *192.168.1.x* is the IP address of your Ubuntu 16 VM)

5. Open a terminal and execute ```$ make``` to see a list of available make shortcuts

6. Instruct the Ubuntu 16 VM to install updates and build Mininet from source for Python 3 with:

    ```$ make setup-ubuntu-vm```

7. Wait endlessly. Maybe watch a show or call a friend.
    
    If you see an error similar to:
    
     ```Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), is another process using it?```,
     
     ... your Ubuntu VM is probably still updating.

8. Reboot the VM

9. Run the topology test with:

    ```$ make topo```
    
    You should see a message upon success, and a png render of the topology at "repo/render/topology.png"

10. Run all other tests with:
    
    ```$ make run```
    
    You should see various outputs (hopefully) proving that our Ryu hub, switch, and QoS switch seem to be working.
    
    Also you'll [TODO: describe log output that proves success]

## General Notes

### Repo Layout

* The ***controllers*** subdirectory contains our Ryu controllers (the main point of this project)

* The ***nodes*** subdirectory contains Python classes that implement functionality of our various nodes, such as:
    * File Server and Client
    * Video Server and Client
    * The Tattle Tail node
    * Supporting base classes

* The ***scripts*** subdirectory contains misc setup scripts

Of our controllers, we have the following source files:

* *Demo_SimpleSwitch.py* is code ripped directly from a tutorial site, and used as our inspiration. This is ***not*** to be considered our original work, and will not be integrated in the final test run configuration.
* *DumbHub.py* is a controller implementing a simple hub, that merely broadcasts all packets received. Should hopefully suffer from congestion issues.
* *SimpleSwitch.py* is one step above the *DumbHub*. It will learn MAC addresses and will maintain a forwarding table that allows it to send traffic only to the most appropriate output port.
* *QSwitch.py* is one step above the *SimpleSwitch*. It will attempt to prioritize UDP packets over TCP packets.

### Explanation of tests

The tests invoked via ```make run``` are designed to prove our controllers are working as intended.
Each test will use one of the above controllers, and is named after the controller used.

You'll know a test is being run by a big group of asterisks appearing in the console with the test's name.
For example, when the *Demo* test is being run (code not writte by us but that helps us prove our framework is functioning correctly) you might see:

```
[558 Final Project][INFO] [Apr 29, 2020; 04:24PM.33] ****************************************
[558 Final Project][INFO] [Apr 29, 2020; 04:24PM.33] ***** Running test with: demo
[558 Final Project][INFO] [Apr 29, 2020; 04:24PM.33] ****************************************
```

Also, each test has its own folder in the *log* subdirectory of our repo, for easier inspection / proof.

Here are the tests that should run:

* The ***Demo*** test is not our own code and should not be considered part of our delivery. It only exists here to help us debug/design/verify our general framework (i.e., all things not Ryu)

* The ***Hub*** test should show lower aggregate bandwidth than with the SimpleSwitch test.
    * The File Server/Client nodes should appear to be splitting the bandwidth with the Video Server/Client nodes
    * There may also be a little slowdown due to congestion / collisions.
    * The Tattle Tail node should also show that it received quite a bit of broadcasted data

* The ***Switch*** test should show higher aggregate bandwidth than with the ***DumbHub*** test.
    * The File Server/Client nodes sholud not appear to be splitting line bandwidth, but only the max aggregate bandwidth of the switch.
    * The Tattle Tail node should report very little stray broadcast data as compared with the ***DumbHub*** test.

* The ***QSwitch*** test should generally present the same as the ***SimpleSwitch*** test, with one exception:
    * The Video Server/Client nodes should show significantly more bandwidth than the File Server/Client nodes.

### Mininet

Mininet seems to be configured for only Python2 by default, and doesn't build correctly on Ubuntu 19.

We also needed to use Python 3 to get Ryu working properly.

Therefore, Mininet shouldn't be installed from repos, but instead built from scratch on Ubuntu 16.

#### Installation on Ubuntu 16.04

Mininet has problems building on newer versions of Ubuntu,
    so we used Ubuntu 16.04.
A basic procedure is as follows:

* Create fresh installation of Ubuntu 16.04 inside VirtualBox
    * Make sure to set bridged networking or some mode so the VM can pull updates, and is visible by your machine
    * Probably want to create the machine on an SSD so updates/config don't take forever (or at least the VDI file)
    * Probably want to use VirtualBox (not KVM) so we can do a Snapshot ***just*** after updates are installed, to decrease the hassle of running installation tests over and over and over again.

* Install, Start SSH daemon, Add SSH key
    * ```$ sudo apt install openssh-server -y && sudo systemctl start sshd```
    * Add your SSH key to the root account's authorized_keys file to avoid entering your password

* Open a terminal in this repo
    * Set/export the environment variable UBUNTU_VM_HOST to point to the VM's IP or hostname
    * Execute the make recipe to setup the VM: ```make setup-ubuntu-vm```
    * Execute the make recipe to run the topology test: ```make topo```
    * Execute the make recipe to run all other tests: ```make run```

## Team Instructions

Mostly we can follow the ***Professor Instructions*** above.
This section is only for extra helpful information.

Your host machine will send commands to the Ubuntu 16 VM over SSH. Before the Ubuntu 16 VM will accept commands from your host machine, you'll need to make sure the VM's *root* account is setup properly. This means one of either:
1. Setting up a password for the root account, if you're okay entering that password for each command/test.
2. Setting up password SSH logins for the root account, if you'd like more seamless execution.

Here's a tutorial for setting root's password:
https://www.cyberciti.biz/faq/change-root-password-ubuntu-linux/

Here's a tutorial for enabling root login over SSH:
https://linuxconfig.org/enable-ssh-root-login-on-ubuntu-16-04-xenial-xerus-linux-server-desktop

Here is some discussion related to enabling SSH keys (passwordless login) to the root account:
https://askubuntu.com/questions/115151/how-to-set-up-passwordless-ssh-access-for-root-user


