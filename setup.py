#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages

import gnome_next_meeting_applet

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="Chmouel Boudjnah",
    author_email='chmouel@chmouel.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="An applet to show next meeting in Gnome",
    entry_points={
        'console_scripts': [
            'gnome-next-meeting-applet=gnome_next_meeting_applet.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    keywords='gnome_next_meeting_applet',
    name='gnome_next_meeting_applet',
    packages=find_packages(
        include=['gnome_next_meeting_applet', 'gnome_next_meeting_applet.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    data_files=[('images/', ["images/before_event.svg", "images/in_event.png"])],
    include_package_data=True,
    tests_require=test_requirements,
    url='https://github.com/chmouel/gnome-next-meeting-applet',
    version=gnome_next_meeting_applet.__version__,
    zip_safe=False,
)
