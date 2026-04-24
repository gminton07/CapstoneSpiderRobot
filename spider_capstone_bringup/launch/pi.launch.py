from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

"""
Launcher for remote Pi
Use with bringup/gui_launcher.py

Requires ssh-key setup between local and remote machines
Gabe's is ~/.ssh/capstone
Used ssh-keygen -> make new ssh key
     ssh-copy-id -> use ssh key to login to the Pi
"""

def generate_launch_description():
    # Launch arguments
    use_mock_hardware = LaunchConfiguration('use_mock_hardware')
    core_group = LaunchConfiguration('core_group') # controls Core group
    use_sensors = LaunchConfiguration('use_sensors') # Controls sensor group
    gait_node = LaunchConfiguration('gait_node')
    
    declare_use_mock = DeclareLaunchArgument(
        'use_mock_hardware',
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
    declare_gait_node = DeclareLaunchArgument(
        'gait_node',
        default_value="ActionSteppy"
    )

    # Config paths
    model_path = PathJoinSubstitution([
        FindPackageShare('spider_capstone_description'),
        'urdf',
        'spider_v2.urdf.xacro'
    ])

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare('spider_capstone_bringup'),
        'config',
        'spider_capstone_controllers.yaml'
    ])

    robot_desc_param = {'robot_description': Command([
        'xacro ',
        model_path,
        ' use_mock_hardware:=',
        use_mock_hardware
    ])}


    # -----------------------------
    # Core Group (conditional)
    # -----------------------------
    core_group = GroupAction(
        condition=IfCondition(core_group),
        actions=[

            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[robot_desc_param]
            ),

            Node(
                package='controller_manager',
                executable='ros2_control_node',
                name='controller_manager',
                parameters=[robot_desc_param, controllers_yaml]
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

    # Gait Node
    gait_node = Node(
        package="spider_capstone_trajectory",
        executable=gait_node
    )

    # -----------------------------
    # Launch Description
    # -----------------------------
    return LaunchDescription([
        declare_use_mock,
        declare_core_group,
        declare_use_sensors,
        declare_gait_node,
        core_group,
        sensor_group,
        gait_node
    ])