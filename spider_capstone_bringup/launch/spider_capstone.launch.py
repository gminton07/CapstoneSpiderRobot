from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # -----------------------------
    # Launch arguments
    # -----------------------------
    use_mock_hardware = LaunchConfiguration('use_mock_hardware')
    use_ui = LaunchConfiguration('use_ui')  # controls UI group
    core_group = LaunchConfiguration('core_group') # controls Core group

    declare_use_mock = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='false'
    )

    declare_use_ui = DeclareLaunchArgument(
        'use_ui',
        default_value='false'
    )

    declare_core_group = DeclareLaunchArgument(
        'core_group',
        default_value='true'
    )

    # -----------------------------
    # Paths
    # -----------------------------
    model_path = PathJoinSubstitution([
        FindPackageShare('spider_capstone_description'),
        'urdf',
        'spider.urdf.xacro'
    ])

    rviz_config_path = PathJoinSubstitution([
        FindPackageShare('spider_capstone_description'),
        'rviz',
        'STL_path_marker.rviz'
    ])

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare('spider_capstone_bringup'),
        'config',
        'spider_capstone_controllers.yaml'
    ])

    # -----------------------------
    # Core Group (always or conditional separately if desired)
    # -----------------------------
    core_group = GroupAction(
        condition=IfCondition(core_group),
        actions=[

            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[{
                    'robot_description': Command([
                        'xacro ',
                        model_path,
                        ' use_mock_hardware:=',
                        use_mock_hardware
                    ])
                }]
            ),

            Node(
                package='spider_capstone_sensors',
                executable='joy_controller'
            ),

            Node(
                package='controller_manager',
                executable='ros2_control_node',
                parameters=[controllers_yaml]
            ),

            # Controller spawners
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster']
            ),

            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_trajectory_controller_1']
            ),

            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_trajectory_controller_2']
            ),

            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_trajectory_controller_3']
            ),

            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_trajectory_controller_4']
            ),
        ]
    )

    # -----------------------------
    # UI Group (conditional)
    # -----------------------------
    ui_group = GroupAction(
        condition=IfCondition(use_ui),
        actions=[

            Node(
                package='joy',
                executable='joy_node'
            ),

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
    # Launch Description
    # -----------------------------
    return LaunchDescription([
        declare_use_mock,
        declare_use_ui,
        declare_core_group,
        core_group,
        ui_group
    ])
