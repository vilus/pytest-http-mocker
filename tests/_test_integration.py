import pytest
import requests
import time


@pytest.fixture
def create_mock_a(http_mocker):
    http_mocker.create_mocks({'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'})


@pytest.fixture
def create_mock_b(http_mocker):
    http_mocker.create_mocks([
        {'name': 'hi_b', 'route': '/b', 'method': 'get', 'responses': 'Hi_b'},
        {'name': 'hi_c', 'route': '/q', 'method': 'get', 'responses': 'Hi_c'},
    ])


@pytest.fixture
def create_mock_c(http_mocker):
    http_mocker.create_mocks({'name': 'hi_c', 'route': '/c', 'method': 'get', 'responses': 'Hi_cx', 'ttl': 1})


@pytest.mark.usefixtures("create_mock_a")
@pytest.mark.run(order=1)
def test_a():
    resp = requests.get('http://127.0.0.1:8080/mocker_api/mocks/')
    print(resp.json())
    # TODO: check mock values
    time.sleep(2)


@pytest.mark.usefixtures("create_mock_b")
@pytest.mark.run(order=8)
def test_b():
    resp = requests.get('http://127.0.0.1:8080/mocker_api/mocks/')
    print(resp.json())
    # TODO: check mock values
    time.sleep(2)


@pytest.mark.xfail(raises=RuntimeError, reason='cause mock ttl = 1')
@pytest.mark.usefixtures("create_mock_c")
def test_c():
    time.sleep(2)


@pytest.mark.usefixtures("create_mock_a")
def test_d():
    time.sleep(1)


@pytest.mark.run(order=4)
def test_n():
    time.sleep(1)


@pytest.mark.run(order=3)
def test_o():
    time.sleep(1)


@pytest.mark.run(order=2)
def test_p():
    time.sleep(1)


@pytest.mark.run(order=1)
def test_r():
    time.sleep(1)
