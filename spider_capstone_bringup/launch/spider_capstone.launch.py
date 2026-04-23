from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # -----------------------------
    # Launch arguments
    # -----------------------------
    use_mock_hardware = LaunchConfiguration('use_mock_hardware')
    use_gui = LaunchConfiguration('use_gui')  # controls gui group
    core_group = LaunchConfiguration('core_group') # controls Core group
    use_sensors = LaunchConfiguration('use_sensors') # Controls sensor group
    use_joy = LaunchConfiguration('use_joy')

    declare_use_mock = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='false'
    )

    declare_use_gui = DeclareLaunchArgument(
        'use_gui',
        default_value='false'
    )

    declare_core_group = DeclareLaunchArgument(
        'core_group',
        default_value='true'
    )

    declare_use_sensors = DeclareLaunchArgument(
        # If true: use sensors, auto_controller
        # If false: use joy, joy_controller
        'use_sensors',
        default_value='true'
    )

    declare_use_joy = DeclareLaunchArgument(
        'use_joy',
        default_value='false'
    )

    # -----------------------------
    # Paths
    # -----------------------------
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

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare('spider_capstone_bringup'),
        'config',
        'spider_capstone_controllers.yaml'
    ])

    # -----------------------------
    # Core Group (conditional)
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
    # Sensor Group (conditional)
    # -----------------------------
    sensor_group = GroupAction(
        condition = IfCondition(use_sensors),
        actions=[
            Node(
                package='spider_capstone_sensors',
                executable='camera_node'
            ),
            Node(
                package='spider_capstone_sensors',
                executable='icm_node'
            ),
            Node(
                package='spider_capstone_sensors',
                executable='auto_controller'
            ),
            Node(
                package='spider_capstone_sensors',
                executable='Ultrasonic_node'
            )
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
        declare_use_mock,
        declare_use_gui,
        declare_core_group,
        declare_use_sensors,
        declare_use_joy,
        core_group,
        gui_group,
        sensor_group,
        joy_group,
    ])
