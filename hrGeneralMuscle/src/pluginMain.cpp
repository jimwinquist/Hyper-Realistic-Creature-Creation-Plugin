/////////////////////////////////////////////////////////////////////////////
//
// hrGeneralMuscleNode.cpp
// Paul Thuriot
// copywrite 2009
// 
// Python plugin for:
// HYPER REAL 2 book - 2009
//
// Convert back to C++: Webber Huang
// 
// 
// NOTE: Tested on Win (32/ 64) and Linux for Maya 8.5, 2008, +
// 
// References:
// 
// Anatomy Based Modeling of the Human Musculature, Ferdi Scheepers, Richard E. Parent. Wayne E. Carlson and Stephen F. May; SIGGRAPH '97
//
/////////////////////////////////////////////////////////////////////////////

#include "hrGeneralMuscleNode.h"

#include <maya/MFnPlugin.h>

#define __AUTHOR__       "Webber Huang"
#define __VERSION__      "1.0"

MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj, __AUTHOR__, __VERSION__, "Any");

	status = plugin.registerNode( "hrGeneralMuscle", hrGeneralMuscle::id, hrGeneralMuscle::creator,
								  hrGeneralMuscle::initialize );
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode( hrGeneralMuscle::id );
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
