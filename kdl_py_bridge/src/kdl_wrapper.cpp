#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <kdl_parser/kdl_parser.hpp>
#include <kdl/tree.hpp>
#include <kdl/chain.hpp>

namespace py = pybind11;

// Helper to parse URDF and return KDL tree
KDL::Tree tree_from_xml(const std::string& xml) {
	KDL::Tree tree;
	if (!kdl_parser::treeFromString(xml, tree)){
		throw std::runtime_error("Failed to extract KDL tree from XML");
	}
	return tree;
}

PYBIND11_MODULE(kdl_wrapper, m) {
	m.doc() = "C++ wrapper for kdl_parser";

	// Bind the Tree class (what we need)
	py::class_<KDL::Tree>(m, "Tree")
		.def(py::init<>())
		.def("getNrOfSegments", &KDL::Tree::getNrOfSegments)
		.def("getChain", [](KDL::Tree& self, const std::string& root, const std::string& tip) {
			KDL::Chain chain;
			self.getChain(root, tip, chain);
			return chain;
		});

	// Bind the Chain class
	py::class_<KDL::Chain>(m, "Chain")
		.def(py::init<>())
		.def("getNrOfJoints", &KDL::Chain::getNrOfJoints)
		.def("getNrOfSegments", &KDL::Chain::getNrOfSegments);

	m.def("tree_from_xml", &tree_from_xml, "Convert URDF XML string to KDL tree.");
}
