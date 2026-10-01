import csv
from pathlib import Path

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool


class SafetyResultEvaluatorNode(Node):
    def __init__(self):
        super().__init__("safety_result_evaluator_node")

        self.declare_parameter("battery_threshold", 0.20)
        self.declare_parameter(
            "output_path",
            "results/safety_evaluation.csv",
        )

        self.battery_threshold = float(
            self.get_parameter("battery_threshold").value
        )
        self.output_path = Path(
            self.get_parameter("output_path").value
        )

        self.sensor_fault = None
        self.battery_percentage = None
        self.safety_return = None
        self.saved = False

        self.create_subscription(
            Bool, "/sensor_fault", self.sensor_callback, 10
        )
        self.create_subscription(
            BatteryState, "/battery_state", self.battery_callback, 10
        )
        self.create_subscription(
            Bool, "/safety_return", self.return_callback, 10
        )

        self.get_logger().info("Safety result evaluator started")

    def sensor_callback(self, message):
        self.sensor_fault = message.data
        self.evaluate()

    def battery_callback(self, message):
        self.battery_percentage = message.percentage
        self.evaluate()

    def return_callback(self, message):
        self.safety_return = message.data
        self.evaluate()

    def evaluate(self):
        if self.saved:
            return

        if (
            self.sensor_fault is None
            or self.battery_percentage is None
            or self.safety_return is None
        ):
            return

        battery_low = (
            self.battery_percentage <= self.battery_threshold
        )
        expected_return = self.sensor_fault or battery_low
        verdict = "PASS" if expected_return == self.safety_return else "FAIL"

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        new_file = not self.output_path.exists()

        with self.output_path.open("a", newline="") as file:
            writer = csv.writer(file)

            if new_file:
                writer.writerow([
                    "sensor_fault",
                    "battery_percentage",
                    "expected_return",
                    "actual_return",
                    "verdict",
                ])

            writer.writerow([
                self.sensor_fault,
                f"{self.battery_percentage:.2f}",
                expected_return,
                self.safety_return,
                verdict,
            ])

        self.get_logger().info(
            f"Evaluation: sensor_fault={self.sensor_fault}, "
            f"battery={self.battery_percentage:.2f}, "
            f"expected={expected_return}, "
            f"actual={self.safety_return}, {verdict}"
        )

        self.saved = True


def main(args=None):
    rclpy.init(args=args)

    node = SafetyResultEvaluatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

