#include <gmock/gmock.h>
#include <memory>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "pluginlib/class_loader.hpp"
#include <cstdlib>

using hardware_interface::SystemInterface;

TEST(SpiderHardwareTest, LoadPlugin) {
	setenv("AMENT_PREFIX_PATH", getenv("AMENT_PREFIX_PATH"), 1);
	pluginlib::ClassLoader<SystemInterface> loader(
			"spider_capstone_hardware",
			"hardware_interface::SystemInterface");

	EXPECT_NO_THROW({
		auto hw = loader.createSharedInstance(
			"spider_capstone_hardware/SpiderHardwareInterface");
	});
}

TEST(SpiderHardwareTest, InitAndExportInterfaces) {
	pluginlib::ClassLoader<SystemInterface> loader(
		"spider_capstone_hardware",
		"hardware_interface::SystemInterface");

	auto hw = loader.createSharedInstance("spider_capstone_hardware/SpiderHardwareInterface");

	// Fake hardware info
	hardware_interface::HardwareComponentInterfaceParams params;
	hardware_interface::HardwareInfo info;

	hardware_interface::ComponentInfo joint;
	joint.name = "joint1";

	joint.command_interfaces.push_back(
		{"position", ""});

	joint.state_interfaces.push_back(
		{"position", "velocity", ""});

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
