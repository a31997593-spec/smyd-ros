from setuptools import find_packages, setup

package_name = "smyd_vint_safety"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="seoyeon",
    maintainer_email="seoyeon@example.com",
    description="Safety return decision node",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "safety_decision_node = "
            "smyd_vint_safety.safety_decision_node:main",
            "sensor_fault_simulator_node ="
            "smyd_vint_safety.sensor_fault_simulator_node:main",
"battery_simulator_node = "
"smyd_vint_safety.battery_simulator_node:main",
 "safety_result_evaluator_node = "
        "smyd_vint_safety.safety_result_evaluator_node:main",

        ],
    },
)



