#
#  Copyright (c) 2016-2022 Deephaven Data Labs and Patent Pending
#

from typing import Dict, List

from .start_jvm import start_jvm

# This is explicitly not a JObjectWrapper, as that would require importing deephaven and jpy
# before the JVM was running.
class Server:
    """
    Represents a Deephaven server that can be created from Python.
    """

    instance = None

    @property
    def j_object(self):
        return self.j_server

    def __init__(self, port:int = 8080, jvm_args:List[str] = None, dh_args: Dict[str, str] = {}):
        """
        Creates a Deephaven embedded server. Only one instance can be created at this time.
        """
        # TODO deephaven-core#2453 consider providing @dataclass for arguments

        # If the server was already created, emit an error to warn away from trying again
        if Server.instance is not None:
            from deephaven import DHError
            raise DHError('Cannot create more than one instance of the server')
        # given the jvm args, ensure that the jvm has started
        start_jvm(jvm_args=jvm_args)

        # it is now safe to import jpy
        import jpy

        # Create a wrapped java server that we can reference to talk to the platform
        self.j_server = jpy.get_type('io.deephaven.python.server.EmbeddedServer')(port, dh_args)

        # Keep a reference to the server so we know it is running
        Server.instance = self

    def start(self):
        """
        Starts the server. Presently once the server is started, it cannot be stopped until the
        python process halts.
        """
        self.j_server.start()
