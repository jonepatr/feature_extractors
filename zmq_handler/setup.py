#!/usr/bin/env python

from distutils.core import setup

setup(
    name="Feature Extractors zmq communicator",
    version="0.1",
    author="Patrik Jonell",
    author_email="pjjonell@kth.se",
    install_requires=["pyzmq", "backports.tempfile", "msgpack", "click"],
    packages=["fe_zmq_server"]
)
