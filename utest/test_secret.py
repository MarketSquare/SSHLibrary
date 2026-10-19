from unittest import mock

import pytest

robot_types = pytest.importorskip("robot.api.types")
Secret = getattr(robot_types, "Secret", None)
if Secret is None:
    pytest.skip("Secret needs Robot Framework 7.4 or newer", allow_module_level=True)

from SSHLibrary import SSHLibrary
from SSHLibrary.library import _reveal


def library_with_connection():
    lib = SSHLibrary()
    client = mock.MagicMock()
    client.config.escape_ansi = False
    client.login.return_value = ""
    client.login_with_public_key.return_value = ""
    lib._connections.register(client)
    return lib, client


def test_reveal_unwraps_secret():
    assert _reveal(Secret("hunter2")) == "hunter2"


@pytest.mark.parametrize("value", ["plain", 22, None, ""])
def test_reveal_keeps_other_values(value):
    assert _reveal(value) == value


def test_open_connection_accepts_secret_host():
    with mock.patch("SSHLibrary.library.SSHClient") as client_class:
        client_class.return_value.config = mock.MagicMock()
        SSHLibrary().open_connection(Secret("secret.host"))
    assert client_class.call_args.args[0] == "secret.host"


def test_login_accepts_secret_username_and_password():
    lib, client = library_with_connection()
    lib.login(Secret("johndoe"), Secret("secretpasswd"))
    assert client.login.call_args.args[:2] == ("johndoe", "secretpasswd")


def test_login_with_public_key_accepts_secrets():
    lib, client = library_with_connection()
    lib.login_with_public_key(Secret("johndoe"), Secret("/keys/id_rsa"), Secret("phrase"))
    assert client.login_with_public_key.call_args.args[:3] == (
        "johndoe",
        "/keys/id_rsa",
        "phrase",
    )
