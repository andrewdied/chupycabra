""" The message format is described in section 5 of RFC 6121.
"""


import chupycabra
import time


body_text = """This is a message
               with two lines."""
body_text_2 = ' This is different body yext'
subject_text = 'This is a very nice subject.'
subject_text_2 = ' This is additional subject text.'


def test_create_message():
    msg = chupycabra.Message()
    assert msg.__str__() == '<message />'


def test_message_create_body_after():
    msg = chupycabra.Message()
    msg.setBody(body_text)
    assert msg.getBody() == body_text


def test_message_create_body_during():
    msg = chupycabra.Message(body=body_text)
    assert msg.getBody() == body_text


def test_message_create_body_twice():
    msg = chupycabra.Message(body=body_text)
    msg.setBody(body_text_2)
    assert msg.getBody() == body_text + body_text_2


def test_message_create_subject_after():
    msg = chupycabra.Message()
    msg.setSubject(subject_text)
    assert msg.getSubject() == subject_text


def test_message_create_subject_during():
    msg = chupycabra.Message(subject=subject_text)
    assert msg.getSubject() == subject_text


def test_message_create_subject_twice():
    msg = chupycabra.Message(subject=subject_text)
    msg.setSubject(subject_text_2)
    assert msg.getSubject() == subject_text + subject_text_2


def test_message_create_thread():
    msg = chupycabra.Message()
    msg.setThread('thread-1')
    assert msg.getThread() == 'thread-1'


def test_message_get_timestamp():
    msg = chupycabra.Message()
    assert msg.time_stamp


def test_message_set_timestamp():
    msg = chupycabra.Message()
    val = time.strftime('%Y%m%dT%H:%M:%S', time.gmtime(time.time()))
    msg.setTimestamp(val)
    assert msg.time_stamp == val


def test_messagae_build_reply():
    msg = chupycabra.Message(frm='romeo@montague.net/venice')
    msg_reply = msg.build_reply(reply_txt='Where for art thou, Romeo?')
    assert msg_reply.__str__() == "<message to='romeo@montague.net/venice'><body>Where for art thou, Romeo?</body></message>"
