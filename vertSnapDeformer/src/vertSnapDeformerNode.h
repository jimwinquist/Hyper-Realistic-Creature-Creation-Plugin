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

#ifndef _vertSnapDeformerNode
#define _vertSnapDeformerNode

#include <maya/MPxDeformerNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MTypeId.h> 

#include <maya/MItGeometry.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>

 
class vertSnapDeformer : public MPxDeformerNode
{
public:
						vertSnapDeformer();
	virtual				~vertSnapDeformer(); 

	virtual MStatus		deform( MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix, unsigned int mIndex );

	static  void*		creator();
	static  MStatus		initialize();

private:
	void                initVertMapping(MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix, unsigned int mIndex);
	int                 getClosestPt( const MPoint& pt, const MPointArray& points );

public:

	static  MObject		driver_mesh;          // driver object (the one the verts will snap to)
	static  MObject		initialized_data;     // allows the vert mapping to be reset
	static  MObject		vert_map;             // this is the array of associated vert indexes (interal node use)

	static	MTypeId		id;
};

#endif
