from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution 
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package = 'spider_capstone_description'

    # CLI launch arguments:
    model = LaunchConfiguration('model')
    rviz_config = LaunchConfiguration('rviz_config')
    use_gui = LaunchConfiguration('gui')

    # Robot description
    robot_description = Command([
        'xacro ', 
        PathJoinSubstitution([
            FindPackageShare(package),
            'urdf',
            model
        ])
    ])

    return LaunchDescription([

        # Declared arguments
        DeclareLaunchArgument(
            'model',
            default_value='spider.urdf.xacro',
            description='URDF/Xacro file'
            ),

        DeclareLaunchArgument(
            'rviz_config',
            default_value='STL_small.rviz',
            description="RViz configuration file"
            ),

        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Use joint_state_publisher_gui'
        ),

        # Nodes
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description
                }]
            ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            condition=IfCondition(use_gui),
            output='screen'
            ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=[
                '-d',
                PathJoinSubstitution([
                    FindPackageShare(package),
                    'rviz',
                    rviz_config
                    ])
                ],
            output='screen'
            ),

    ])
