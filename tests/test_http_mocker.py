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
def one_mock(testdir):
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


def test_create_one_mock(one_mock):
    result = one_mock.runpytest()
    assert result.ret == 0


mocked_two = """
@pytest.fixture(scope="session", autouse=True)
def mocked_srv(monkeypatch_session):
    MockedMockServer = MagicMock(
        return_value=MagicMock(**{'create_mocks.return_value': [
            MagicMock(**{'delete.return_value': {'is_expired': False}}),
            MagicMock(**{'delete.return_value': {'is_expired': False}})
        ]})
    )

    monkeypatch_session.setattr('pytest_http_mocker.MockServer', MockedMockServer)
"""


@pytest.fixture
def two_mocks(testdir):
    testdir.makepyfile(monkey_session_fixture + mocked_two + """
def test_create_two_mocks(http_mocker):
    http_mocks_param = [
        {'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'},
        {'name': 'hi_b', 'route': '/b', 'method': 'get', 'responses': 'Hi_b'},
    ]

    http_mocker.create_mocks(http_mocks_param)

    assert http_mocker.srv.create_mocks.call_count == 1  # only 1
    assert http_mocker.srv.create_mocks.call_args == ((http_mocks_param,),)
    assert len(http_mocker.created_mocks) == 2
    """)
    return testdir


def test_create_two_mocks(two_mocks):
    result = two_mocks.runpytest()
    assert result.ret == 0


mocked_failed = """
@pytest.fixture(scope="session", autouse=True)
def mocked_srv(monkeypatch_session):
    MockedMockServer = MagicMock(
        return_value=MagicMock(**{'create_mocks.side_effect': IOError})
    )

    monkeypatch_session.setattr('pytest_http_mocker.MockServer', MockedMockServer)
"""


@pytest.fixture
def failed_mock(testdir):
    testdir.makepyfile(monkey_session_fixture + mocked_failed + """
def test_failed_create_two_mock(http_mocker):
    http_mocks_param = [
        {'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'},
        {'name': 'hi_b', 'route': '/b', 'method': 'get', 'responses': 'Hi_b'},
    ]

    with pytest.raises(RuntimeError):
        http_mocker.create_mocks(http_mocks_param)

    assert http_mocker.srv.create_mocks.call_count == 3
    assert http_mocker.srv.create_mocks.call_args == ((http_mocks_param,),)
    assert len(http_mocker.created_mocks) == 0
    """)
    return testdir


def test_failed_create_mocks(failed_mock):
    result = failed_mock.runpytest('--mocker-retries', '3', '--mocker-retry-waittime', '0')
    assert result.ret == 0


@pytest.fixture
def passing_options(testdir):
    testdir.makepyfile("""
def test_passing_options(http_mocker):
    # TODO: avoid high coupling
    assert http_mocker.srv.url == 'http://test_passing_opts:1234/api/'
    assert http_mocker.default_retries == 2
    assert http_mocker.default_retry_waittime == 10
    """)
    return testdir


def test_passing_options(passing_options):
    result = passing_options.runpytest('--mocker-retries', '2',
                                       '--mocker-retry-waittime', '10',
                                       '--mocker-url', 'http://test_passing_opts:1234/api/')
    assert result.ret == 0


@pytest.fixture
def delete_mocks(testdir):
    testdir.makepyfile(monkey_session_fixture + mocked_two + """
def test_delete_mocks(http_mocker):
    http_mocks_param = [
        {'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'},
        {'name': 'hi_b', 'route': '/b', 'method': 'get', 'responses': 'Hi_b'},
    ]

    http_mocker.create_mocks(http_mocks_param)
    http_mocker.delete_mocks()

    for m in http_mocker.created_mocks:
        assert m.delete.call_count == 1
    """)
    return testdir


def test_delete_mocks(delete_mocks):
    result = delete_mocks.runpytest()
    assert result.ret == 0


@pytest.fixture
def delete_mocks_negative(testdir):
    testdir.makepyfile(monkey_session_fixture + """
@pytest.fixture(scope="session", autouse=True)
def mocked_srv(monkeypatch_session):
    MockedMockServer = MagicMock(
        return_value=MagicMock(**{'create_mocks.return_value': [
            MagicMock(**{'delete.side_effect': IOError}),
            MagicMock(**{'delete.return_value': {'is_expired': True}}),
            MagicMock(**{'delete.return_value': {'is_expired': False}}),
        ]})
    )

    monkeypatch_session.setattr('pytest_http_mocker.MockServer', MockedMockServer)


def test_delete_mocks_negative(http_mocker):
    http_mocker.create_mocks([])

    with pytest.raises(RuntimeError) as excinfo:
        http_mocker.delete_mocks()

    errs_msg = ' '.join(excinfo.value.args[0])
    assert 'on delete: ' in errs_msg
    assert 'expired mock: ' in errs_msg

    for m in http_mocker.created_mocks:
        assert m.delete.call_count == 1

    http_mocker.created_mocks = []
    """)
    return testdir


def test_delete_mocks_negative(delete_mocks_negative):
    result = delete_mocks_negative.runpytest()
    assert result.ret == 0


@pytest.fixture
def failed_delete_mocks_on_teardown(testdir):
    testdir.makepyfile(monkey_session_fixture + """
@pytest.fixture(scope="session", autouse=True)
def mocked_srv(monkeypatch_session):
    MockedMockServer = MagicMock(
        return_value=MagicMock(**{'create_mocks.return_value': [
            MagicMock(**{'delete.side_effect': IOError}),
        ]})
    )

    monkeypatch_session.setattr('pytest_http_mocker.MockServer', MockedMockServer)


def test_failed_delete_mocks_on_teardown(http_mocker):
    http_mocks_param = [
        {'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'},
        {'name': 'hi_b', 'route': '/b', 'method': 'get', 'responses': 'Hi_b'},
    ]

    http_mocker.create_mocks(http_mocks_param)
    """)
    return testdir


def test_failed_delete_mocks_on_teardown(failed_delete_mocks_on_teardown):
    result = failed_delete_mocks_on_teardown.runpytest('--mocker-retries', '1', '--mocker-retry-waittime', '0')
    assert 'E           RuntimeError: [" on delete:' in result.stdout.str()
    result.stdout.fnmatch_lines(['__________ ERROR at teardown of test_failed_delete_mocks_on_teardown ___________'])
    assert result.ret == 1
