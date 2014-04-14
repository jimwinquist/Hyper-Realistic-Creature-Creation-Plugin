/////////////////////////////////////////////////////////////////////////////
// vertSnapDeformer
// originally from Writing Creature Deformers
// Erick Miller
// copywrite 2009
// 
// converted to python -- Paul Thuriot
// converted back to c++ -- Webber Huang
// 
// Python plugin for:
// HYPER REAL 2 book - 2009
// 
// 
// 
// NOTE: Tested on Win (32/ 64) and Linux for Maya 8.5, 2008, +
/////////////////////////////////////////////////////////////////////////////

#include "vertSnapDeformerNode.h"

#include <maya/MFnPlugin.h>

#define __AUTHOR__       "Webber Huang"
#define __VERSION__      "1.0"

MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj, __AUTHOR__, __VERSION__, "Any");

	status = plugin.registerNode( "vertSnapDeformer", vertSnapDeformer::id, vertSnapDeformer::creator,
								  vertSnapDeformer::initialize, MPxNode::kDeformerNode );
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

	status = plugin.deregisterNode( vertSnapDeformer::id );
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
