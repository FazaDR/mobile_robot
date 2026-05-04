import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
	pkg_share = get_package_share_directory("mobile_robot")
	xacro_file = os.path.join(pkg_share, "model", "robot.xacro")
	bridge_params = os.path.join(pkg_share, "parameters", "bridge_parameters.yaml")

	use_sim_time = LaunchConfiguration("use_sim_time")
	gz_args = LaunchConfiguration("gz_args")

	robot_description = Command(["xacro", " ", xacro_file])

	gz_sim = IncludeLaunchDescription(
		PythonLaunchDescriptionSource(
			os.path.join(
				get_package_share_directory("ros_gz_sim"),
				"launch",
				"gz_sim.launch.py",
			)
		),
		launch_arguments={"gz_args": gz_args}.items(),
	)

	robot_state_publisher = Node(
		package="robot_state_publisher",
		executable="robot_state_publisher",
		parameters=[
			{"use_sim_time": use_sim_time, "robot_description": robot_description}
		],
		output="screen",
	)

	spawn_robot = Node(
		package="ros_gz_sim",
		executable="create",
		arguments=[
			"-world",
			"default",
			"-name",
			"ddmr",
			"-string",
			robot_description,
		],
		output="screen",
	)

	bridge = Node(
		package="ros_gz_bridge",
		executable="parameter_bridge",
		parameters=[{"config_file": bridge_params}],
		output="screen",
	)

	return LaunchDescription(
		[
			DeclareLaunchArgument(
				"use_sim_time", default_value="true", description="Use sim time"
			),
			DeclareLaunchArgument(
				"gz_args",
				default_value="-r -v 4",
				description="Arguments passed to gz sim; use -r -s -v 4 for headless",
			),
			gz_sim,
			robot_state_publisher,
			TimerAction(period=8.0, actions=[spawn_robot]),
			bridge,
		]
	)
