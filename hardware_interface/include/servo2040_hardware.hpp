// ROS2 Hardware interface for servo2040
// 
// 

#ifndef SPIDER_CAPSTONE_HARDWARE__SERVO2040_HPP
#define SPIDER_CAPSTONE_HARDWARE__SERVO2040_HPP

#include "hardware_interface/system_interface.hpp"

using hardware_interface::return_type;

namespace spider_capstone_hardware
{
    using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

    class RobotSystem : public hardware_interface::SystemInterface
    {
        public:
            CallbackReturn on_init(
                const hardware_interface::HardwareComponentIterfaceParams & params) override;
            CallbackReturn on_configure() override;
            return_type read() override;
            return_type write() override;

        protected:
    };

} // namespace spider_capstone_hardware

#endif // SPIDER_CAPSTONE_HARDWARE__SERVO2040
