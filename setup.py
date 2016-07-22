from setuptools import setup

with open('README.rst') as f:
    readme = f.read()


with open('LICENSE') as f:
    license = f.read()


setup(
    name='nova-mksproxy',
    version='0.0.1',
    description='Nova console proxy for VMware instances',
    long_description=readme,
    author='VMware Inc.',
    author_email='rgerganov@vmware.com',
    url='https://github.com/rgerganov/nova-mksproxy',
    license=license,
    entry_points = {
        'console_scripts': ['nova-mksproxy=novaproxy.mksproxy:main'],
    },
    packages=['novaproxy'],
    install_requires=['websockify', 'python-novaclient']
)
