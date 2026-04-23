from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

"""
Launcher for local machine
Use with bringup/gui_launcher.py
"""

def generate_launch_description():
    # Launch arguments
    use_gui = LaunchConfiguration('use_gui')  # controls gui group
    use_joy = LaunchConfiguration('use_joy')
    
    declare_use_gui = DeclareLaunchArgument(
        'use_gui',
        default_value='false'
    )
    declare_use_joy = DeclareLaunchArgument(
        'use_joy',
        default_value='false'
    )

    # Config paths
    model_path = PathJoinSubstitution([
        FindPackageShare('spider_capstone_description'),
        'urdf',
        'spider_v2.urdf.xacro'
    ])

    rviz_config_path = PathJoinSubstitution([
        FindPackageShare('spider_capstone_description'),
        'rviz',
        'STL_path_marker.rviz'
    ])

    # -----------------------------
    # gui Group (conditional)
    # -----------------------------
    gui_group = GroupAction(
        condition=IfCondition(use_gui),
        actions=[

            Node(
                package='rviz2',
                executable='rviz2',
                output='screen',
                arguments=['-d', rviz_config_path]
            ),

            Node(
                package='spider_capstone_visualize',
                executable='joint_trajectory_plot'
            ),
        ]
    )

    # -----------------------------
    # Joy Group (conditional)
    # -----------------------------
    joy_group = GroupAction(
        condition = IfCondition(use_joy),
        actions=[
            Node(
                package='joy',
                executable='joy_node'
            ),

            Node(
                package='spider_capstone_sensors',
                executable='joy_controller'
            ),
        ]
    )    

    # -----------------------------
    # Launch Description
    # -----------------------------
    return LaunchDescription([
        declare_use_gui,
        declare_use_joy,
        gui_group,
        joy_group
    ])