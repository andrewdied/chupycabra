from chupycabra.chupycabra import Connection

conn = Connection(host='localhost', port=5222, namespace='NS_TEST')
# Client uses NS_CLIENT as the namespace


def test_create_connection():
    assert isinstance(conn, Connection)


def test_oneup():
    number = conn.getAnID()
    assert number == u'1'
    number = conn.getAnID()
    assert number == u'2'