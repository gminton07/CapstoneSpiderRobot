cmake_minimum_required(VERSION 3.8)
project(kdl_py_bridge)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(kdl_parser REQUIRED)
find_package(orocos_kdl REQUIRED)
find_package(pybind11_vendor REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# add include directory for KDL
include_directories(
	include
	${orocos_kdl_INCLUDE_DIRS}
	${kdl_parser_INCLUDE_DIRS}
)

# create C++ shared library for python
pybind11_add_module(kdl_wrapper src/kdl_wrapper.cpp)

target_link_libraries(kdl_wrapper PRIVATE
	kdl_parser::kdl_parser
	${orocos_kdl_LIBRARIES}
)

set(PYTHON_INSTALL_DEST "lib/python3.12/site-packages")

# installation into python site-packages path
install(TARGETS kdl_wrapper
	DESTINATION ${PYTHON_INSTALL_DEST}
)

ament_package()
