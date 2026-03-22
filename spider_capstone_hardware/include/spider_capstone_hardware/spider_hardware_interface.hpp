#ifndef SPIDER_CAPSTONE_HARDWARE__SPIDER_HARDWARE_INTERFACE_HPP
#define SPIDER_CAPSTONE_HARDWARE__SPIDER_HARDWARE_INTERFACE_HPP

// Include library headers
// Standard libraries
#include <memory>
#include <string>
#include <vector>

// ROS2 libraries
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace spider_capstone_hardware
{

	class SpiderHardwareInterface : public hardware_interface::SystemInterface
	{
		public:
			RCLCPP_SHARED_PTR_DEFINITIONS(SpiderHardwareInterface)

			SpiderHardwareInterface() = default;
			~SpiderHardwareInterface() override = default;

			// Lifecycle methods
			hardware_interface::CallbackReturn on_init(
					const hardware_interface::HardwareComponentInterfaceParams& params) override;

			hardware_interface::CallbackReturn on_configure(
					const rclcpp_lifecycle::State &previous_state) override;

			hardware_interface::CallbackReturn on_cleanup(
					const rclcpp_lifecycle::State &previous_state) override;

			hardware_interface::CallbackReturn on_shutdown(
					const rclcpp_lifecycle::State &previous_state) override;

			hardware_interface::CallbackReturn on_activate(
					const rclcpp_lifecycle::State &previous_state) override;

			hardware_interface::CallbackReturn on_deactivate(
					const rclcpp_lifecycle::State &previous_state) override;

			hardware_interface::CallbackReturn on_error(
					const rclcpp_lifecycle::State &previous_state) override;

			// Interface export methods
			std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

			std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

			// Read & Write methods
			hardware_interface::return_type read(
					const rclcpp::Time &time,
					const rclcpp::Duration &period) override;

			hardware_interface::return_type write(
					const rclcpp::Time &time,
					const rclcpp::Duration &period) override;
				
		private:
			// Storage vectors
			std::vector<double> hw_positions_;
			std::vector<double> hw_velocities_;
			std::vector<double> hw_commands_;
	};

} // namespace spider_capstone_hardware


#endif // SPIDER_CAPSTONE_HARDWARE__SPIDER_HARDWARE_INTERFACE_HPP
