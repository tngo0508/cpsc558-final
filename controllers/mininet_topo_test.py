from mininet.topo import Topo


class MyTopo(Topo):
    "Simple topology example."

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        file_server = self.addHost('FS')
        video_server = self.addHost('VS')
        tattle_tail = self.addHost('TT')
        file_client = self.addHost('FC')
        video_client = self.addHost('VC')
        dumb_hub = self.addSwitch('S1')

        # Add links
        self.addLink(dumb_hub, file_server)
        self.addLink(dumb_hub, video_server)
        self.addLink(dumb_hub, tattle_tail)
        self.addLink(dumb_hub, file_client)
        self.addLink(dumb_hub, video_client)

        # self.addLink(file_server, dumb_hub)
        # self.addLink(video_server, dumb_hub)
        # self.addLink(tattle_tail, dumb_hub)
        # self.addLink(file_client, dumb_hub)
        # self.addLink(video_client, dumb_hub)

topos = {'mytopo': (lambda: MyTopo())}

