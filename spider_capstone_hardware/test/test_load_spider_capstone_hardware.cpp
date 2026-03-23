#include <gmock/gmock.h>
#include <memory>
#include <cstdlib>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "pluginlib/class_loader.hpp"

using hardware_interface::SystemInterface;

TEST(SpiderHardwareTest, LoadPlugin) {
	// <-- Corrected to "hardware_interface"
	pluginlib::ClassLoader<SystemInterface> loader(
			"hardware_interface",
			"hardware_interface::SystemInterface");

	EXPECT_NO_THROW({
		auto hw = loader.createSharedInstance(
			"spider_capstone_hardware/SpiderHardwareInterface");
	});
}

TEST(SpiderHardwareTest, InitAndExportInterfaces) {
	// <-- Corrected to "hardware_interface"
	pluginlib::ClassLoader<SystemInterface> loader(
		"hardware_interface",
		"hardware_interface::SystemInterface");

	auto hw = loader.createSharedInstance("spider_capstone_hardware/SpiderHardwareInterface");

	// Fake hardware info
	hardware_interface::HardwareComponentInterfaceParams params;
	hardware_interface::HardwareInfo info;

	hardware_interface::ComponentInfo joint;
	joint.name = "joint1";

	// Changed to direct struct assignments for cleaner compatibility across versions
	hardware_interface::InterfaceInfo pos_cmd;
	pos_cmd.name = "position";
	joint.command_interfaces.push_back(pos_cmd);

	hardware_interface::InterfaceInfo pos_state;
	pos_state.name = "position";
	joint.state_interfaces.push_back(pos_state);

	hardware_interface::InterfaceInfo vel_state;
	vel_state.name = "velocity";
	joint.state_interfaces.push_back(vel_state);

	info.joints.push_back(joint);
	params.hardware_info = info;

	// Initialize
	ASSERT_EQ(
		hw->on_init(params),
		hardware_interface::CallbackReturn::SUCCESS);

	// Export interfaces
	auto states = hw->export_state_interfaces();
	auto commands = hw->export_command_interfaces();

	EXPECT_EQ(states.size(), 2);
	EXPECT_EQ(commands.size(), 1);
}
