#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <kdl_parser/kdl_parser.hpp>
#include <kdl/tree.hpp>
#include <kdl/chain.hpp>
#include <kdl/jntarray.hpp>
#include <kdl/chainidsolver_recursive_newton_euler.hpp>
#include <kdl/chainfksolverpos_recursive.hpp>
#include <kdl/frames.hpp>

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
			if (self.getChain(root, tip, chain)) throw std::runtime_error("Chain not found between specified links.");
			return chain;
		});

	// Bind the Chain class
	py::class_<KDL::Chain>(m, "Chain")
		.def(py::init<>())
		.def("getNrOfJoints", &KDL::Chain::getNrOfJoints)
		.def("getNrOfSegments", &KDL::Chain::getNrOfSegments)
		.def("getSegment", 
			(const KDL::Segment& (KDL::Chain::*)(unsigned int) const) &KDL::Chain::getSegment,
			py::return_value_policy::reference_internal);

	// Bind the Joint class
    py::class_<KDL::Joint>(m, "Joint")
        .def("getName", &KDL::Joint::getName)
		.def("getTypeName", &KDL::Joint::getTypeName);

    // Bind the Segment class
    py::class_<KDL::Segment>(m, "Segment")
        .def("getJoint", &KDL::Segment::getJoint)
        .def("getName", &KDL::Segment::getName);

	// Get JntArray class
	py::class_<KDL::JntArray>(m, "JntArray")
        .def(py::init<unsigned int>())
        .def("rows", &KDL::JntArray::rows)
        .def("__setitem__", [](KDL::JntArray &self, int i, double v) {
            if (i < 0 || i >= (int)self.rows()) throw py::index_error();
            self(i) = v;
        })
        .def("__getitem__", [](const KDL::JntArray &self, int i) {
            if (i < 0 || i >= (int)self.rows()) throw py::index_error();
            return self(i);
        });

	// Get Vector (for Gravity)
    py::class_<KDL::Vector>(m, "Vector")
        .def(py::init<double, double, double>())
		.def_property_readonly("x", [](const KDL::Vector& v) {return v.x();})
		.def_property_readonly("y", [](const KDL::Vector& v) {return v.y();})
		.def_property_readonly("z", [](const KDL::Vector& v) {return v.z();});

	// Rotation (roll, pitch, yaw)
	py::class_<KDL::Rotation>(m, "Rotation")
		.def("GetRPY", [](const KDL::Rotation& r) {
			double roll, pitch, yaw;
			r.GetRPY(roll, pitch, yaw);
			return py::make_tuple(roll, pitch, yaw);
		});

	// Frame (Pose containing Vector p and Rotation m)
	py::class_<KDL::Frame>(m, "Frame")
		.def(py::init<>())
		.def_property_readonly("p", [](const KDL::Frame& f) {return f.p; })
		.def_property_readonly("M", [](const KDL::Frame& f) {return f.M; });

	// Forward kinematics (position)
	py::class_<KDL::ChainFkSolverPos_recursive>(m, "ChainFkSolverPos_recursive")
		.def(py::init<const KDL::Chain&>())
		.def("JntToCart", [](KDL::ChainFkSolverPos_recursive& self, const KDL::JntArray& q_in) {
			KDL::Frame p_out;
			int status = self.JntToCart(q_in, p_out);
			if (status < 0) {
				throw std::runtime_error("FK Solver failed to calculate pose.");
			}
			return p_out;
		});
		
    // Get Inverse Dynamics Solver (RNE)
    py::class_<KDL::ChainIdSolver_RNE>(m, "ChainIdSolver_RNE")
        .def(py::init<KDL::Chain, KDL::Vector>())
        .def("CartToJnt", [](KDL::ChainIdSolver_RNE &self, 
                             const KDL::JntArray &q, const KDL::JntArray &v, 
                             const KDL::JntArray &a, const std::vector<KDL::Wrench> &f_ext, 
                             KDL::JntArray &torques) {
            return self.CartToJnt(q, v, a, f_ext, torques);
        });

	m.def("tree_from_xml", &tree_from_xml, "Convert URDF XML string to KDL tree.");
}
