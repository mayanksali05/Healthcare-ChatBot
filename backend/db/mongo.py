"""MongoDB connection layer.

This module only establishes and verifies a connection. It deliberately does
NOT create collections, indexes or documents - MongoDB creates a database
lazily on the first write, so as long as nothing here writes, the server stays
empty. Add a separate repository module when there is actually data to store.

The connection string is read from the environment and never hardcoded, so
credentials for a real cluster (Atlas, or a managed instance) stay out of the
repository. In deployment, source MONGODB_URI from the secret store rather
than a .env file.
"""

import os

# The driver is optional at import time: the chat endpoint does not need Mongo,
# so a missing pymongo must not stop the whole app from starting. The health
# endpoint reports the missing driver instead.
try:

    from pymongo import MongoClient
    from pymongo.errors import PyMongoError

    DRIVER_AVAILABLE = True

except ImportError:

    MongoClient = None

    class PyMongoError(Exception):
        pass

    DRIVER_AVAILABLE = False


# Local development default. A URI with credentials must come from the
# environment - never commit one.
DEFAULT_URI = "mongodb://localhost:27017"

DEFAULT_DB_NAME = "healthcare_chatbot"

# Fail fast instead of hanging the request thread when mongod is not running.
SERVER_SELECTION_TIMEOUT_MS = 3000

CONNECT_TIMEOUT_MS = 3000


_client = None


def get_uri():

    return os.getenv("MONGODB_URI", DEFAULT_URI)


def get_db_name():

    return os.getenv("MONGODB_DB_NAME", DEFAULT_DB_NAME)


def redact(uri):
    """Hide any credentials before a URI reaches a log line or an API response."""

    if "@" not in uri:

        return uri

    scheme, _, rest = uri.partition("://")

    _, _, host = rest.rpartition("@")

    return f"{scheme}://***:***@{host}"


def get_client():
    """Return the shared client, creating it on first use.

    MongoClient is thread safe and pools connections internally, so one
    instance is shared across requests.
    """

    global _client

    if not DRIVER_AVAILABLE:

        raise RuntimeError(
            "pymongo is not installed. Run: pip install -r requirements.txt"
        )

    if _client is None:

        _client = MongoClient(
            get_uri(),
            serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=CONNECT_TIMEOUT_MS,
            appname="healthcare-chatbot",
        )

    return _client


def get_database():
    """Return a database handle.

    This performs no I/O and does not create the database - Mongo only
    materialises it when something is written.
    """

    return get_client()[get_db_name()]


def ping():
    """Check connectivity. Returns a status dict instead of raising."""

    if not DRIVER_AVAILABLE:

        return {
            "connected": False,
            "uri": redact(get_uri()),
            "database": get_db_name(),
            "error": "pymongo is not installed. Run: pip install -r requirements.txt",
        }

    try:

        get_client().admin.command("ping")

        return {
            "connected": True,
            "uri": redact(get_uri()),
            "database": get_db_name(),
        }

    except PyMongoError as error:

        return {
            "connected": False,
            "uri": redact(get_uri()),
            "database": get_db_name(),
            "error": str(error),
        }


def server_info():
    """Version and a collection count, for the health endpoint.

    list_collection_names() is a read - it stays empty until something writes.
    """

    status = ping()

    if not status["connected"]:

        return status

    try:

        info = get_client().server_info()

        collections = get_database().list_collection_names()

        return {
            **status,
            "version": info.get("version"),
            "collections": collections,
            "collection_count": len(collections),
        }

    except PyMongoError as error:

        return {**status, "connected": False, "error": str(error)}


def close():

    global _client

    if _client is not None:

        _client.close()

        _client = None


if __name__ == "__main__":

    from pprint import pprint

    print(f"\nConnecting to {redact(get_uri())} ...\n")

    pprint(server_info())

    close()
