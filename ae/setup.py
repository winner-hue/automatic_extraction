#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

'''
打包
'''

setup(
    name="automatic_extraction",
    version="0.1",
    author="winner-hue",
    author_email="1344246287@qq.com",
    description=("automatic extraction"),
    long_description=("automatic extraction"),
    license="MIT License",
    keywords="automatic extract",
    url="https://github.com/winner-hue/automatic_extraction",
    packages=['ae.extraction', 'ae'],
    # 需要安装的依赖
    install_requires=[
        "lxml>=4.6.2",
        "numpy>=1.20.1",
        "PyYAML>=5.4.1",
        "dateparser>=0.7.6"
    ],
    zip_safe=False
)
