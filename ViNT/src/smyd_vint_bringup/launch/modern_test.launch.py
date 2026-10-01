from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    ros_gz_sim = Path(get_package_share_directory("ros_gz_sim"))
    turtlebot = Path(get_package_share_directory("turtlebot3_description"))

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(ros_gz_sim / "launch" / "gz_sim.launch.py")
            ),
            launch_arguments={"gz_args": "-r empty.sdf"}.items(),
        ),
        Node(
            package="ros_gz_sim",
            executable="create",
            arguments=[
                "-file",
                str(turtlebot / "urdf" / "turtlebot3_waffle_pi.urdf"),
                "-name",
                "waffle_pi",
            ],
            output="screen",
        ),
    ])

