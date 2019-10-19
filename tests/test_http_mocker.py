import pytest


monkey_session_fixture = """
import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope='session')
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch
    m = MonkeyPatch()
    yield m
    m.undo()
"""


@pytest.fixture
def one_mock_test(testdir):
    testdir.makepyfile(monkey_session_fixture + """
@pytest.fixture(scope="session", autouse=True)
def mocked_srv(monkeypatch_session):
    MockedMockServer = MagicMock(
        return_value=MagicMock(**{'create_mocks.return_value': [
            MagicMock(**{'delete.return_value': {'is_expired': False}})
        ]})
    )

    monkeypatch_session.setattr('pytest_http_mocker.MockServer', MockedMockServer)


def test_create_one_mock(http_mocker):
    http_mock_param = {'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'}

    http_mocker.create_mocks(http_mock_param)

    assert http_mocker.srv.create_mocks.call_count == 1  # only 1
    assert http_mocker.srv.create_mocks.call_args == (([http_mock_param],),)
    assert len(http_mocker.created_mocks) == 1
    """)
    return testdir


def test_create_one_mock(one_mock_test):
    result = one_mock_test.runpytest('--mocker-retries', '2', '--mocker-retry-waittime', '2')
    # TODO: add --mocker-url -> check http_mocker.srv.call_args
    assert result.ret == 0
