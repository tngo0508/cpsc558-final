
# Final Project

CPSC 558 - Advanced Networking

## Team Members

* Mike Peralta mikeperalta@csu.fullerton.edu
* Thomas Ngo tngo0508@csu.fullerton.edu

## Code Strategy

Let's use lots of classes to avoid stepping on each others' commits.

Some class suggestions; Let's have a class for each of the following:

* Our custom switch
* Switch MAC-to-PhysicalPort table
* File server
* Video server
* File client
* Video client
* L2 packet (populated with member variables representing the state of an L2 packe)
* L4 packet (populated with member variables representing the state of an L4 packet)
* QoS decisions

## Git Strategy

### Branches

All development should take place on the ***dev*** branch. When our project is in a stable state, we can merge ***dev*** into ***master***.

### Tags

Whenever the ***master*** branch reaches a good state with new features, that could be considered "the best candidate we currently have for professor submission", we can add a git tag.

We should use [Semantic Versioning 2.0.0](https://semver.org/) to name our tags (aka releases).

Long story short; They'd look like this:

* v0.1.0
* v1.0.0
* v1.1.0
* v1.1.1
* etc

## Other Info/Instructions

TODO



