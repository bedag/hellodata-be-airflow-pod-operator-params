from setuptools import setup

setup(
    name='hellodata_pod_operator_params',
    description='This package aims to simplify the usage of airflow k8s pod operator',
    url='https://github.com/felix-bedag/pod-operator-params',
    author='Felix Neidhart',
    author_email='felix.neidhart@bedag.ch',
    packages=['src.hellodata_pod_operator_params'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
