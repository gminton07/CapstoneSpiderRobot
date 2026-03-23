from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'spider_capstone_trajectory'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gabe',
    maintainer_email='gminton07@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            f'test_jsp = {package_name}.test_jsp:main',
            f'joint_trajectory = {package_name}.joint_trajectory:main',
            f'BigSteppy = {package_name}.BigSteppy:main',
        ],
    },
)
