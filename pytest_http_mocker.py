import pytest
import time

from mocker_client import MockServer


def pytest_addoption(parser):
    group = parser.getgroup('http_mocker')
    group.addoption("--mocker-url", default='http://127.0.0.1:8080/mocker_api/mocks/',
                    help="TODO")
    group.addoption("--mocker-retries", default=10, type=int,
                    help="TODO")
    group.addoption("--mocker-retry-waittime", default=60, type=int,
                    help="TODO")


class HttpMocker:
    def __init__(self, mock_srv=None, default_retries=10, default_retry_waittime=60):
        self.srv = mock_srv if mock_srv else MockServer(url='http://127.0.0.1:8080/mocker_api/mocks/')
        self.default_retries = default_retries
        self.default_retry_waittime = default_retry_waittime
        self.created_mocks = []

    def create_mocks(self, params, *, retries=None, retry_waittime=None):
        if isinstance(params, dict):
            params = [params]

        retries = retries if retries else self.default_retries
        retry_waittime = retry_waittime if retry_waittime else self.default_retry_waittime
        errs = []

        for _ in range(retries):
            try:
                self.created_mocks = self.srv.create_mocks(params)
            except Exception as e:
                errs.append(e)  # TODO: delete dup error
            else:
                break
            time.sleep(retry_waittime)
        else:
            raise RuntimeError(f'failed to create mocks: {errs}')

    def delete_mocks(self):
        unexpected_err = []
        expired_mocks = []

        for m in self.created_mocks:
            try:
                mock_info = m.delete()
            except IOError as e:
                unexpected_err.append(f'{e} on delete: {m.data}')
            else:
                if mock_info['is_expired']:
                    expired_mocks.append(f'expired mock: {m.data}')

        if expired_mocks or unexpected_err:
            raise RuntimeError(expired_mocks + unexpected_err)


@pytest.fixture
def http_mocker(request):
    mocker_url = request.config.getoption('--mocker-url')
    retries = request.config.getoption('--mocker-retries')
    retry_waittime = request.config.getoption('--mocker-retry-waittime')

    mock_srv = MockServer(url=mocker_url)
    http_mocker = HttpMocker(mock_srv=mock_srv,
                             default_retries=retries,
                             default_retry_waittime=retry_waittime)
    yield http_mocker
    http_mocker.delete_mocks()
