import rclpy
from rclpy.node import Node

from sensor_msgs.msg import BatteryState


class BatterySimulatorNode(Node):
    def __init__(self):
        super().__init__("battery_simulator_node")

        self.declare_parameter("initial_percentage", 1.0)
        self.declare_parameter("drain_rate_per_sec", 0.05)

        self.percentage = float(
            self.get_parameter("initial_percentage").value
        )
        self.drain_rate = float(
            self.get_parameter("drain_rate_per_sec").value
        )

        self.percentage = max(0.0, min(1.0, self.percentage))
        self.drain_rate = max(0.0, self.drain_rate)

        self.publisher = self.create_publisher(
            BatteryState,
            "/battery_state",
            10,
        )

        self.create_timer(1.0, self.publish_battery)

        self.get_logger().info(
            f"Battery model started: "
            f"initial={self.percentage:.2f}, "
            f"drain_rate={self.drain_rate:.2f}/sec"
        )

    def publish_battery(self):
        self.percentage = max(
            0.0,
            self.percentage - self.drain_rate,
        )

        message = BatteryState()
        message.percentage = self.percentage
        message.voltage = 12.0 * self.percentage

        self.publisher.publish(message)

        self.get_logger().info(
            f"Battery percentage={self.percentage:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = BatterySimulatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


