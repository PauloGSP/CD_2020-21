"""Tests two clients."""
import pytest
import pexpect
import time

TIMEOUT = 2


@pytest.fixture
def foo():
    foo = pexpect.spawnu("python3 foo.py")
    time.sleep(1)

    assert foo.isalive()
    yield foo

    if foo.isalive():
        foo.sendline("exit")
        foo.close()


@pytest.fixture
def bar():
    bar = pexpect.spawnu("python3 bar.py")
    time.sleep(1)

    assert bar.isalive()
    yield bar

    if bar.isalive():
        bar.sendline("exit")
        bar.close()


def test_hello(foo, bar):
    foo.sendline("Olá Mundo")

    bar.expect("Olá Mundo", timeout=TIMEOUT)
    bar.sendline("Hello World")

    foo.expect("Hello World", timeout=TIMEOUT)


def test_storm(foo, bar):
    foo.sendline("Olá Mundo")

    bar.expect("Olá Mundo", timeout=TIMEOUT)
    bar.sendline("Hello World")
    bar.sendline("How are you?")
    bar.sendline("Are you new around here?")
    bar.sendline("Hope you enjoy your stay")

    foo.expect("Hope you enjoy your stay", timeout=TIMEOUT)
    foo.sendline("You are awesome!")
    foo.expect("You are awesome!", timeout=TIMEOUT)

    bar.expect("You are awesome!", timeout=TIMEOUT)


def test_basic(foo, bar):
    foo.sendline("Hello!")
    bar.expect("Hello!", timeout=TIMEOUT)
    bar.sendline("Welcome aboard")
    bar.sendline("Who are you?")
    foo.expect("Who are you?", timeout=TIMEOUT)
    foo.sendline("I'm Joe")
    bar.expect("Joe", timeout=TIMEOUT)
    bar.sendline("Nice to meet you Joe")
    foo.sendline("Cya around")

    foo.expect("Cya around")
    bar.expect("Cya around")


def test_extra(foo, bar):
    foo.sendline("Hello!")
    bar.expect("Hello!", timeout=TIMEOUT)
    foo.sendline("/join #cd")
    foo.sendline("no one is here...")
    with pytest.raises(pexpect.exceptions.TIMEOUT):
        bar.expect("no one is here", timeout=TIMEOUT)


def test_channels(foo, bar):
    foo.sendline("/join #c1")
    bar.sendline("/join #c2")
    foo.sendline("Hello darkness, my old friend")
    foo.sendline("/join #c2")
    foo.sendline("I've come to talk with you again")
    bar.expect("I've come to talk with you again")
    foo.sendline("/join #c1")
    foo.sendline("Because a vision softly creeping")
    with pytest.raises(pexpect.exceptions.TIMEOUT):
        bar.expect("Because a vision softly creeping", timeout=TIMEOUT)
