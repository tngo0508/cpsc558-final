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

# Logs dir
UBUNTU_VM_LOG_DIR := $(UBUNTU_VM_REPO_DIR)/log

# Topology image
UBUNTU_VM_TOPOLOGY_IMAGE := $(UBUNTU_VM_RENDER_DIR)/topology.png

##### Ubuntu 16.04 Virtual Machine
##################################

#
LOCAL_RENDER_DIR := $(MAKEFILE_DIR)/render
LOCAL_LOG_DIR := $(MAKEFILE_DIR)/log

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


#
$(LOCAL_RENDER_DIR):
	$(call say,Ensuring: $@)
	mkdir --parents "$@"


$(LOCAL_LOG_DIR):
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


# Run our tests and stuff
run:	deploy
run:	clean-mininet-state |
	$(call say,Running our tests and stuff)
	ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && make clean-logs" \
		&& ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --run --run-name demo" \
		&& ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --run --run-name hub" \
		&& ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --run --run-name switch" \
		&& ssh "$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)" "cd \"$(UBUNTU_VM_REPO_DIR)\" && ./main.py --run --run-name qswitch" \
		&& $(MAKE) pull-logs
.PHONY:	run


# Pull logs from the remote server
pull-logs:	|	$(LOCAL_LOG_DIR)
	$(call say,Pulling logs)
	rsync \
		--archive --delete \
		--stats --itemize-changes --human-readable --verbose --progress \
 		"$(UBUNTU_VM_USER)"@"$(UBUNTU_VM_HOST)":"$(UBUNTU_VM_LOG_DIR)"/ "$(LOCAL_LOG_DIR)"/
.PHONY: pull-logs


# Pull logs from the remote server
clean-logs:	|	$(LOCAL_LOG_DIR)
	$(call say,Cleaning logs)
	-rm "$(LOCAL_LOG_DIR)"/* -vr
.PHONY: clean-logs

