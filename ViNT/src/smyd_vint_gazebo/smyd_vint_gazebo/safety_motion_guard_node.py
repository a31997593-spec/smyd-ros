import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Bool


class SafetyMotionGuardNode(Node):
    def __init__(self):
        super().__init__("safety_motion_guard_node")

        self.safety_return = False

        self.create_subscription(
            Bool,
            "/safety_return",
            self.safety_callback,
            10,
        )

        self.create_subscription(
            Twist,
            "/cmd_vel_command",
            self.command_callback,
            10,
        )

        self.safe_command_publisher = self.create_publisher(
            Twist,
            "/cmd_vel_safe",
            10,
        )

        self.create_timer(0.1, self.publish_stop_if_required)

        self.get_logger().info("Safety motion guard started")

    def safety_callback(self, message):
        self.safety_return = message.data

        if self.safety_return:
            self.get_logger().warn(
                "Safety return requested: robot motion stopped"
            )
            self.publish_stop()
        else:
            self.get_logger().info(
                "Safety return cleared: motion commands allowed"
            )

    def command_callback(self, message):
        if not self.safety_return:
            self.safe_command_publisher.publish(message)

    def publish_stop_if_required(self):
        if self.safety_return:
            self.publish_stop()

    def publish_stop(self):
        stop_command = Twist()
        self.safe_command_publisher.publish(stop_command)


def main(args=None):
    rclpy.init(args=args)

    node = SafetyMotionGuardNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


