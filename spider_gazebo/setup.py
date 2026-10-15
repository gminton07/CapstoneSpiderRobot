from os.path import join
from glob import glob
from setuptools import find_packages, setup

package_name = 'spider_gazebo'
share_directory = join('share', package_name)

data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    (share_directory, ['package.xml']),
    (join(share_directory, 'meshes'), glob('meshes/*.stl')),
    (join(share_directory, 'urdf'), glob('urdf/*.urdf.xacro')),
    (join(share_directory, 'launch'), glob('launch/*')),
    (join(share_directory, 'config'), glob('config/*')),
]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files = data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rosuser',
    maintainer_email='rosuser@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
