// Include libraries
// Project header
#include "spider_capstone_hardware/spider_hardware_interface.hpp"

// Standard libraries
#include <algorithm>
#include <limits>

// ROS2 libraries
#include "rclcpp/rclcpp.hpp"

// Define namespace
namespace spider_capstone_hardware {
	
	hardware_interface::CallbackReturn SpiderHardwareInterface::on_init(
			const hardware_interface::HardwareComponentInterfaceParams& params)
	{

		if (hardware_interface::SystemInterface::on_init(params) != hardware_interface::CallbackReturn::SUCCESS)
		{
			return hardware_interface::CallbackReturn::ERROR;
		}

		// Get robot model info and resize arrays
		size_t num_joints = info_.joints.size();

		hw_positions_.resize(num_joints, 0.0);
		hw_velocities_.resize(num_joints, 0.0);
		hw_commands_.resize(num_joints, 0.0);

		RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
				"Initialized with %zu joints.", num_joints);

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_configure(
			const rclcpp_lifecycle::State &)
	{
		RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
				"Configuring hardware...");

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_cleanup(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Cleaning up hardware...");

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_activate(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Activating hardware...");

	  // Reset states to current commands
	  hw_positions_ = hw_commands_;

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_deactivate(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Deactivating hardware...");

	  return hardware_interface::CallbackReturn::SUCCESS;
	}


	hardware_interface::CallbackReturn SpiderHardwareInterface::on_shutdown(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Shutting down hardware...");

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_error(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"),
		       "Error in hardware interface!");

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	std::vector<hardware_interface::StateInterface>
	SpiderHardwareInterface::export_state_interfaces()
	{
	  std::vector<hardware_interface::StateInterface> state_interfaces;

	  for (size_t i = 0; i < info_.joints.size(); ++i)
	  {
	    state_interfaces.emplace_back(
	      hardware_interface::StateInterface(
		info_.joints[i].name, "position", &hw_positions_[i]));

	    state_interfaces.emplace_back(
	      hardware_interface::StateInterface(
		info_.joints[i].name, "velocity", &hw_velocities_[i]));
	  }

	  return state_interfaces;
	}

	std::vector<hardware_interface::CommandInterface>
	SpiderHardwareInterface::export_command_interfaces()
	{
	  std::vector<hardware_interface::CommandInterface> command_interfaces;

	  for (size_t i = 0; i < info_.joints.size(); ++i)
	  {
	    command_interfaces.emplace_back(
	      hardware_interface::CommandInterface(
		info_.joints[i].name, "position", &hw_commands_[i]));
	  }

	  return command_interfaces;
	}

	hardware_interface::return_type SpiderHardwareInterface::read(
	  const rclcpp::Time &,
	  const rclcpp::Duration &)
	{
	  // Fake hardware: just reflect commands as states
	  for (size_t i = 0; i < hw_positions_.size(); ++i)
	  {
	    hw_positions_[i] = hw_commands_[i];
	    hw_velocities_[i] = 0.0;
	  }

	  return hardware_interface::return_type::OK;
	}

	hardware_interface::return_type SpiderHardwareInterface::write(
	  const rclcpp::Time &,
	  const rclcpp::Duration &)
	{
	  return hardware_interface::return_type::OK;
	}

}  // namespace spider_capstone_hardware

// <-- Moved macro OUTSIDE the namespace for correct global linkage
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
		spider_capstone_hardware::SpiderHardwareInterface,
		hardware_interface::SystemInterface)