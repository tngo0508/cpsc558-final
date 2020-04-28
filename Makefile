define say
	$(info [CPSC558 Final] $1)
endef
define die
	$(error [CPSC558 Final] Fatal $1)
endef


##
MAKEFILE_DIR := .
SCRIPTS_DIR := $(MAKEFILE_DIR)/scripts
SCRIPT_SETUP_UBUNTU_VM := $(SCRIPTS_DIR)/setup-ubuntu-vm

##################################
##### Ubuntu 16.04 Virtual Machine

## The "Ubuntu VM" refers to the fresh/empty Ubuntu 16.04 VM you'll make just for this project

# Hostname
UBUNTU_VM_HOST_DEFAULT := 558-ubuntu.vm
ifeq ($(UBUNTU_VM_HOST),)
$(call say,No value in UBUNTU_VM_HOST; Using default)
UBUNTU_VM_HOST := $(UBUNTU_VM_HOST_DEFAULT)
endif
$(call say,Using UBUNTU_VM_HOST: $(UBUNTU_VM_HOST))


# Obviously we must use root for mininet
UBUNTU_VM_USER := root

# Repo dir
UBUNTU_VM_REPO_DIR := /root/Documents/cpsc558-repo

# Render dir
UBUNTU_VM_RENDER_DIR := $(UBUNTU_VM_REPO_DIR)/render

# Topology image
UBUNTU_VM_TOPOLOGY_IMAGE := $(UBUNTU_VM_RENDER_DIR)/topology.png

##### Ubuntu 16.04 Virtual Machine
##################################

#
LOCAL_RENDER_DIR := $(MAKEFILE_DIR)/render


default:	menu

menu:
	@echo
	@echo "**************************************************"
	@echo "**************************************************"
	@echo "********** CPSC 558 Final Project Menu"
	@echo
	@echo "make menu              ===> This menu"
	@echo
	@echo "make setup-ubuntu-vm   ===> Setup a fresh Ubuntu 16.04 install (Update, install Mininet, etc)"
	@echo
	@echo "make topo              ===> Run a test build of the topology"
	@echo "make run               ===> Run all our tests and stuff"
	@echo
	@echo "*** OpenFlow Controllers ***"
	@echo "One of the following controllers must be running before our main program can execute."
	@echo "Each of these targets controls how our central \"switch\" behaves."
	@echo
	@echo "make hub               ===> Start a dumb hub controller"
	@echo "make simple-switch     ===> Start a simple switch controller (Ryu, OpenFlow)"
	@echo


#
$(LOCAL_RENDER_DIR):
	$(call say,Ensuring: $@)
	mkdir --parents "$@"


#	Deploy this repo into the Mininet VM
deploy:
	$(call say,Deploying repo to Mininet VM)
	ssh $(UBUNTU_VM_USER)@"$(UBUNTU_VM_HOST)" "mkdir --parents \"$(UBUNTU_VM_REPO_DIR)\"" \
		&& rsync --archive --delete --recursive --verbose --stats --itemize-changes --human-readable --progress \
			"$(MAKEFILE_DIR)"/ $(UBUNTU_VM_USER)@"$(UBUNTU_VM_HOST)":"$(UBUNTU_VM_REPO_DIR)"/


#
setup-ubuntu-vm:	deploy
setup-ubuntu-vm:
	$(call say,Setting up new Ubuntu VM)
	ssh $(UBUNTU_VM_USER)@"$(UBUNTU_VM_HOST)" "cd $(UBUNTU_VM_REPO_DIR) && $(SCRIPT_SETUP_UBUNTU_VM)"
.PHONY: setup-ubuntu-vm


#	Clean mininet state
clean-mininet-state:
	$(call say,Cleaning Mininet state)
	-ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "mn -c && killall python3"
.PHONY: clean-mininet-state


#	Topology Test
topo:	deploy
topo:	topology
topology:	clean-mininet-state | $(LOCAL_RENDER_DIR)
	ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --topo"
	@echo Grabbing the topology image
	scp "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)":"$(UBUNTU_VM_TOPOLOGY_IMAGE)" "$(LOCAL_RENDER_DIR)"
.PHONY:	topo topology


#	Run our tests and stuff
run:	deploy
run:	clean-mininet-state |
	$(call say,Running our tests and stuff)
	ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --run"
.PHONY:	run


#	Start Ryu dumb hub controller
hub:		dumb-hub
dumb-hub:	deploy
dumb-hub:	|
	$(call say,Launching dumb-hub controller (RYU))
	ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ryu-manager DumbHub.py"
.PHONY:	dumb-hub


#	Start Ryu simple switch controller
simple-switch:	deploy
simple-switch:	|
	$(call say,Launching simple switch controller (RYU))
	ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ryu-manager SimpleSwitch"
.PHONY:	simple-switch





