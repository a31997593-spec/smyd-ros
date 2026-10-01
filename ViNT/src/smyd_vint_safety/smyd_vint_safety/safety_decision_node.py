import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from sensor_msgs.msg import BatteryState


class SafetyDecisionNode(Node):
    def __init__(self):
        super().__init__("safety_decision_node")

        self.sensor_fault = False
        self.battery_percentage = 1.0
        self.return_required = False

        self.declare_parameter("battery_threshold", 0.20)
        self.battery_threshold = self.get_parameter(
            "battery_threshold"
        ).value

        self.create_subscription(
            Bool,
            "/sensor_fault",
            self.sensor_fault_callback,
            10,
        )

        self.create_subscription(
            BatteryState,
            "/battery_state",
            self.battery_callback,
            10,
        )

        self.return_publisher = self.create_publisher(
            Bool,
            "/safety_return",
            10,
        )

        self.create_timer(1.0, self.evaluate_safety)

        self.get_logger().info("Safety decision node started")

    def sensor_fault_callback(self, message):
        self.sensor_fault = message.data

    def battery_callback(self, message):
        if message.percentage >= 0.0:
            self.battery_percentage = message.percentage

    def evaluate_safety(self):
        battery_low = (
            self.battery_percentage <= self.battery_threshold
        )

        new_return_required = self.sensor_fault or battery_low

        if new_return_required != self.return_required:
            self.return_required = new_return_required

            if self.return_required:
                self.get_logger().warn(
                    "SAFE RETURN REQUIRED: "
                    f"sensor_fault={self.sensor_fault}, "
                    f"battery={self.battery_percentage:.2f}"
                )
            else:
                self.get_logger().info(
                    "Normal operation resumed"
                )

        output = Bool()
        output.data = self.return_required
        self.return_publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)

    node = SafetyDecisionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


