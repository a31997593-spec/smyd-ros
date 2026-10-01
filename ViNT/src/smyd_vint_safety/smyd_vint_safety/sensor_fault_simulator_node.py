import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool


class SensorFaultSimulatorNode(Node):
    def __init__(self):
        super().__init__("sensor_fault_simulator_node")

        self.declare_parameter("scenario", "normal")
        self.declare_parameter("toggle_interval_sec", 3)

        self.scenario = self.get_parameter("scenario").value
        self.toggle_interval = int(
            self.get_parameter("toggle_interval_sec").value
        )

        self.publisher = self.create_publisher(
            Bool,
            "/sensor_fault",
            10,
        )

        self.fault_state = False
        self.last_published = None
        self.counter = 0

        self.create_timer(1.0, self.publish_fault)

        self.get_logger().info(
            f"Sensor scenario started: {self.scenario}"
        )

    def publish_fault(self):
        if self.scenario == "constant_fault":
            self.fault_state = True

        elif self.scenario == "intermittent_fault":
            self.counter += 1

            if self.counter >= self.toggle_interval:
                self.fault_state = not self.fault_state
                self.counter = 0

        else:
            self.fault_state = False

        message = Bool()
        message.data = self.fault_state
        self.publisher.publish(message)

        if self.last_published != self.fault_state:
            self.get_logger().info(
                f"Published sensor_fault={self.fault_state}"
            )
            self.last_published = self.fault_state


def main(args=None):
    rclpy.init(args=args)

    node = SensorFaultSimulatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

