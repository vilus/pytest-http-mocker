from setuptools import setup

setup(
    name='pytest-http-mocker',
    version='0.0.1',
    description='Pytest plugin for http mocking (via https://github.com/vilus/mocker)',
    url='https://github.com/vilus/pytest-http-mocker',
    author='Shevchenko Vladimir',
    py_modules=['pytest_http_mocker'],
    install_requires=['pytest', 'mocker-client'],
    entry_points={'pytest11': ['http-mocker = pytest_http_mocker', ], },
)
