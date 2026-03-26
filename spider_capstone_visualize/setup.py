from setuptools import find_packages, setup

package_name = 'spider_capstone_visualize'

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
    maintainer='Gabriel Minton',
    maintainer_email='g.m.minton@wustl.edu',
    description='Workspace envelope visualizations',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'leg_2_joint_node = spider_capstone_visualize.leg_workspace_node:main',
            'leg_3_joint_node = spider_capstone_visualize.leg_3_joint_node:main',
            f'joint_trajectory_plot = {package_name}.joint_trajectory_plot:main',
        ],
    },
)
