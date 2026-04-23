cmake_minimum_required(VERSION 3.8)
project(spider_capstone_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# install files
install(
  DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install python programs
install(
  DIRECTORY python/
  DESTINATION lib/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS
)

ament_package()
