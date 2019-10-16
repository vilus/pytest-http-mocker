import pytest
import requests
import time


@pytest.fixture
def create_mock_a(http_mocker):
    http_mocker.create_mocks({'name': 'hi_a', 'route': '/q', 'method': 'get', 'responses': 'Hi_a'})


@pytest.fixture
def create_mock_b(http_mocker):
    http_mocker.create_mocks({'name': 'hi_b', 'route': '/q', 'method': 'get', 'responses': 'Hi_b'})


@pytest.mark.usefixtures("create_mock_a")
@pytest.mark.run(order=1)
def test_a():
    resp = requests.get('http://127.0.0.1:8080/mocker_api/mocks/')
    print('>>>>>>')
    print(resp.json())
    time.sleep(4)


@pytest.mark.flaky(reruns=5, reruns_delay=2)
@pytest.mark.usefixtures("create_mock_b")
@pytest.mark.run(order=8)
def test_b():
    # TODO: ttl=1 and rerunfailures and expired in teardown
    resp = requests.get('http://127.0.0.1:8080/mocker_api/mocks/')
    print('>>>>>>')
    print(resp.json())
    time.sleep(4)


def test_c():
    time.sleep(1)
    pass


def test_d():
    time.sleep(1)
    pass


@pytest.mark.run(order=4)
def test_n():
    time.sleep(1)
    pass


@pytest.mark.run(order=3)
def test_o():
    time.sleep(1)
    pass


@pytest.mark.run(order=2)
def test_p():
    time.sleep(1)
    pass


@pytest.mark.run(order=1)
def test_r():
    time.sleep(1)
    pass
