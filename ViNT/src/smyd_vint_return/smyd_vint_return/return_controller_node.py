import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool


def clamp(value, limit):
    return max(-limit, min(limit, value))


class ReturnControllerNode(Node):
    def __init__(self):
        super().__init__("return_controller_node")

        self.home_x = 0.0
        self.home_y = 0.0
        self.battery_threshold = 0.20

        self.pose = None
        self.odom_time = None
        self.battery = None
        self.battery_time = None
        self.sensor_fault = None
        self.fault_time = None
        self.safety_return = None
        self.safety_time = None
        self.command = None
        self.command_time = None
        self.arrived = False
        self.last_state = None

        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_subscription(BatteryState, "/battery_state", self.on_battery, 10)
        self.create_subscription(Bool, "/sensor_fault", self.on_fault, 10)
        self.create_subscription(Bool, "/safety_return", self.on_safety, 10)
        self.create_subscription(Twist, "/cmd_vel_command", self.on_command, 10)

        self.publisher = self.create_publisher(Twist, "/cmd_vel_safe", 10)
        self.create_timer(0.1, self.control)
        self.get_logger().info("Return controller started; home=(0, 0)")

    def on_odom(self, msg):
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        p = msg.pose.pose.position
        self.pose = (p.x, p.y, yaw)
        self.odom_time = time.monotonic()

    def on_battery(self, msg):
        self.battery = msg.percentage
        self.battery_time = time.monotonic()

    def on_fault(self, msg):
        self.sensor_fault = msg.data
        self.fault_time = time.monotonic()

    def on_safety(self, msg):
        self.safety_return = msg.data
        self.safety_time = time.monotonic()

    def on_command(self, msg):
        self.command = msg
        self.command_time = time.monotonic()

    def set_state(self, state):
        if state != self.last_state:
            self.get_logger().info(state)
            self.last_state = state

    def control(self):
        now = time.monotonic()
        output = Twist()

        ready = (
            self.pose is not None
            and self.odom_time is not None
            and now - self.odom_time < 1.0
            and self.battery_time is not None
            and now - self.battery_time < 2.5
            and self.fault_time is not None
            and now - self.fault_time < 2.5
            and self.safety_time is not None
            and now - self.safety_time < 2.5
        )

        if not ready:
            self.set_state("Waiting for fresh odom, battery, fault and safety topics")
        elif self.sensor_fault:
            self.set_state("Sensor fault: stopped")
        elif self.arrived:
            self.set_state("Home reached: stopped")
        elif self.safety_return:
            if self.battery is None or self.battery > self.battery_threshold:
                self.set_state("Safety requested for unknown reason: stopped")
            else:
                x, y, yaw = self.pose
                dx = self.home_x - x
                dy = self.home_y - y
                distance = math.hypot(dx, dy)

                if distance <= 0.05:
                    self.arrived = True
                    self.set_state("Home reached: stopped")
                else:
                    target_yaw = math.atan2(dy, dx)
                    error = math.atan2(
                        math.sin(target_yaw - yaw),
                        math.cos(target_yaw - yaw),
                    )
                    if abs(error) > 0.20:
                        output.angular.z = clamp(1.5 * error, 0.4)
                        self.set_state("Returning: turning toward home")
                    else:
                        output.linear.x = min(0.10, 0.5 * distance)
                        output.angular.z = clamp(error, 0.4)
                        self.set_state("Returning: driving toward home")
        elif (
            self.command is not None
            and self.command_time is not None
            and now - self.command_time < 0.5
        ):
            output = self.command
            self.set_state("Normal: forwarding command")
        else:
            self.set_state("Normal: no recent command, stopped")

        self.publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = ReturnControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()



if __name__ == "__main__":
    main()

