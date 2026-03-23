// Include libraries
// Project header
#include "spider_capstone_hardware/spider_hardware_interface.hpp"

// Standard libraries
#include <algorithm>
#include <limits>
#include <cstring>
#include <sstream>

// Linux POSIX serial headers
// For the serial communications
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

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
				"Configuring hardware and opening serial port...");

		// Open serial port
		serial_fd_ = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_SYNC);

		if (serial_fd_ < 0) {
			RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"),
					"Failed to open /dev/ttyACM0. Check permissions ad path.");
			return hardware_interface::CallbackReturn::ERROR;
		}

		// Configure serial port (115200 baud, 8N1)
		struct termios tty;
		if (tcgetattr(serial_fd_, &tty) != 0) {
			RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"), "Error from tcgetattr.");
			return hardware_interface::CallbackReturn::ERROR;
		}

		cfsetospeed(&tty, B115200);
		cfsetispeed(&tty, B115200);

		tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; 	// 8-bit chars
		tty.c_cflag |= (CLOCAL | CREAD); 		// Ignore modem controls, enable reading
		tty.c_cflag &= ~(PARENB | PARODD); 		// Shut off parity
		tty.c_cflag &= ~CSTOPB;
		tty.c_cflag &= ~CRTSCTS;

		tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON);
		tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
		tty.c_oflag &= ~OPOST;

		// Fetch bytes as they are available
		tty.c_cc[VMIN] = 0;
		tty.c_cc[VTIME] = 1; // 0.1 second read timeout

		if (tcsetattr(serial_fd_, TCSANOW, &tty) != 0) {
			RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"), "Error from tcsetattr");
			return hardware_interface::CallbackReturn::ERROR;
		}

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_cleanup(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Cleaning up hardware, closing serial port...");

	  if (serial_fd_ >= 0) {
		  close(serial_fd_);
		  serial_fd_ = -1;
	  }

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_activate(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Activating hardware...");

	  // Send the enable command to the hardware
	  std::string response = send_and_receive("ENABLE\n");

	  if (response.empty()) {
		  RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"),
				  "Hardware failed to respond to activation");
		  return hardware_interface::CallbackReturn::ERROR;
	  }

	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"), 
			  "Hardware activated successfully. Response: %s", response.c_str());

	  // Reset states to current commands
	  hw_positions_ = hw_commands_;

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_deactivate(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Deactivating hardware...");

	  // Send disable command
	  std::string response = send_and_receive("DISABLE\n");

	  if (response.empty()) {
		  RCLCPP_WARN(rclcpp::get_logger("SpiderHardwareInterface"),
				  "Hardware failed to respond to deactivation");
	  } else {
		  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
				  "Hardware deactivated. Response: %s", response.c_str());
	  }

	  return hardware_interface::CallbackReturn::SUCCESS;
	}


	hardware_interface::CallbackReturn SpiderHardwareInterface::on_shutdown(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_INFO(rclcpp::get_logger("SpiderHardwareInterface"),
		      "Shutting down hardware...");

	  if (serial_fd_ >= 0) {
		  close(serial_fd_);
		  serial_fd_ = -1;
	  }

	  return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn SpiderHardwareInterface::on_error(
	  const rclcpp_lifecycle::State &)
	{
	  RCLCPP_ERROR(rclcpp::get_logger("SpiderHardwareInterface"),
		       "Error in hardware interface!");

	  if (serial_fd_ >= 0) {
		  close(serial_fd_);
		  serial_fd_ = -1;
	  }

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

	std::string SpiderHardwareInterface::send_and_receive(const std::string& msg)
	{
		if (serial_fd_ < 0) return "";
		 
		// Using global ::write to avoid naming conflicts with our write method
		::write(serial_fd_, msg.c_str(), msg.length());

		char read_buf [256];
		memset(&read_buf, '\0', sizeof(read_buf));

		// Use global ::read
		int num_bytes = ::read(serial_fd_, &read_buf, sizeof(read_buf));

		if (num_bytes > 0) {
			return std::string(read_buf, num_bytes);
		}

		// If all else fails:
		return "";
	}

	hardware_interface::return_type SpiderHardwareInterface::read(
	  	const rclcpp::Time &,
	  	const rclcpp::Duration &)
	{
		// We expect an immediate response (ping-pong) immediately
		// during write(), so this can pass instead.

	  	return hardware_interface::return_type::OK;
	}

	hardware_interface::return_type SpiderHardwareInterface::write(
	  	const rclcpp::Time &,
	  	const rclcpp::Duration &)
	{
		if (serial_fd_ < 0) {
			return hardware_interface::return_type::ERROR;
		}

		// Build space-separated command string
		// Format: "CMD <pos1> <pos2> ... \n"
		std::ostringstream command_stream;
		command_stream << "MOVE";

		for (size_t i = 0; i < hw_commands_.size(); ++i)
		{
			command_stream << " " << hw_commands_[i];
		}
		command_stream << "\n";

		// Send the message and wait for the response
		std::string response = send_and_receive(command_stream.str());

		if (!response.empty()) {
			// Update state interfaces with current command interface values
			hw_positions_ = hw_commands_;
		} else {
			// Variable to throttle warning logger messages
			static auto last_warn_time = std::chrono::steady_clock::now();
			auto now = std::chrono::steady_clock::now();
			
			if (now - last_warn_time >= std::chrono::seconds(1)) {
				RCLCPP_WARN(rclcpp::get_logger("SpiderHardwareInterface"),
						"No response received from hardware during write cycle");
				last_warn_time = now;
			}
		}

	  	return hardware_interface::return_type::OK;
	}

}  // namespace spider_capstone_hardware

// <-- Moved macro OUTSIDE the namespace for correct global linkage
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
		spider_capstone_hardware::SpiderHardwareInterface,
		hardware_interface::SystemInterface)
