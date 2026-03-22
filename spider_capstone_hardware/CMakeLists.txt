cmake_minimum_required(VERSION 3.8)
project(spider_capstone_hardware)

# -----------------------
# Compiler settings
# -----------------------
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# -----------------------
# Dependencies
# -----------------------
find_package(ament_cmake REQUIRED)

find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)

# -----------------------
# Library
# -----------------------
add_library(${PROJECT_NAME} SHARED
  src/spider_hardware_interface.cpp
)

target_include_directories(${PROJECT_NAME}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
)

# -----------------------
# Install
# -----------------------
install(
  TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  FILES plugin.xml
  DESTINATION share/${PROJECT_NAME}
)

# -----------------------
# Plugin export (AFTER install!)
# -----------------------
pluginlib_export_plugin_description_file(
  hardware_interface
  plugin.xml
)

# -----------------------
# Testing
# -----------------------
if(BUILD_TESTING)
  find_package(ament_cmake_gmock REQUIRED)

  ament_add_gmock(test_spider_hardware
    test/test_load_spider_capstone_hardware.cpp
  )

  target_link_libraries(test_spider_hardware
    ${PROJECT_NAME}
  )

  ament_target_dependencies(test_spider_hardware
    hardware_interface
    pluginlib
    rclcpp
  )

  add_dependencies(test_spider_hardware ${PROJECT_NAME})

  # Ensure pluginlib can see installed package
  set_tests_properties(test_spider_hardware PROPERTIES
    ENVIRONMENT "AMENT_PREFIX_PATH=${CMAKE_INSTALL_PREFIX}"
  )
endif()

# -----------------------
# Export
# -----------------------
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_libraries(${PROJECT_NAME})

ament_export_dependencies(
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
)

ament_package()