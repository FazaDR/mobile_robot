#!/usr/bin/env python3
import os
import sys
import time
import subprocess

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from std_msgs.msg import String


def main():
    rclpy.init()
    node = Node('publish_robot_description')

    qos = QoSProfile(depth=1)
    qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
    pub = node.create_publisher(String, 'robot_description', qos)

    # find xacro file in package share
    try:
        pkg_share = subprocess.check_output(['ros2', 'pkg', 'prefix', 'mobile_robot']).decode().strip()
    except Exception:
        pkg_share = os.path.join(os.environ.get('HOME', '/home'), 'ws_mr', 'install', 'mobile_robot', 'share', 'mobile_robot')

    xacro_path = os.path.join(pkg_share, 'model', 'robot.xacro')
    if not os.path.exists(xacro_path):
        node.get_logger().error(f'robot.xacro not found at {xacro_path}')
        rclpy.shutdown()
        return

    try:
        xml = subprocess.check_output(['xacro', xacro_path]).decode()
    except Exception as e:
        node.get_logger().error(f'failed to run xacro: {e}')
        rclpy.shutdown()
        return

    msg = String()
    msg.data = xml

    # publish a few times so latched subscribers can receive
    for _ in range(5):
        pub.publish(msg)
        node.get_logger().info('Published robot_description')
        time.sleep(0.2)

    # keep node alive briefly so create can subscribe
    time.sleep(2.0)
    node.get_logger().info('Shutting down publisher')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
