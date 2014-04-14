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

#include <maya/MFnData.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MArrayDataBuilder.h>

#include <maya/MGlobal.h>
#include <maya/MItMeshVertex.h>

// CHANGE THIS ID AS NEEDED
MTypeId     vertSnapDeformer::id( 0x7269b );
MObject     vertSnapDeformer::driver_mesh;        
MObject     vertSnapDeformer::initialized_data;       
MObject     vertSnapDeformer::vert_map;   

vertSnapDeformer::vertSnapDeformer() {}
vertSnapDeformer::~vertSnapDeformer() {}

MStatus vertSnapDeformer::deform( MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix, unsigned int mIndex )
{
	int initialized_mapping = data.inputValue(initialized_data).asShort();

	///////////////////////////////////////
	// Attribute based initializing for resetting the deform state:
	// (using an attr on the node)
	//
	if( initialized_mapping == 1 )
	{
		initVertMapping(data, iter, localToWorldMatrix, mIndex);
		initialized_mapping = data.inputValue( initialized_data ).asShort();
	}

	if( initialized_mapping == 2 )  //deformer data initialized successfully. begin deform.
	{
		//get data from data block:
		float env = data.inputValue( envelope ).asFloat();
		
		MArrayDataHandle vertMapArrayData  = data.inputArrayValue( vert_map );

		// attach to the poly function set :
		MDataHandle meshAttrHandle = data.inputValue( driver_mesh );
		MObject meshMobj  = meshAttrHandle.asMesh();
		MItMeshVertex vertIter( meshMobj );

		// this is the deform loop:
		for( ; !iter.isDone(); iter.next() )
		{
			float weight = weightValue( data, mIndex, iter.index() ); //painted weight
			float ww = weight * env; //weight * envelope value


			if (ww != 0)
			{
				vertMapArrayData.jumpToElement( iter.index() );
				int index_mapped = vertMapArrayData.inputValue().asInt(); //get mapped index

				if( index_mapped >= 0 ) // filter out un-mapped points
				{
					int prevInt;
					vertIter.setIndex(index_mapped, prevInt);

					MPoint mappedPt = vertIter.position( MSpace::kWorld ); // get in world space

					MPoint iterPt = iter.position() * localToWorldMatrix; // get in world space by transforming

					MPoint pt = iterPt + ((mappedPt - iterPt) * ww);    // scale delta for painted weights

					pt = pt * localToWorldMatrix.inverse(); 			// transform new pt back into obj space
					iter.setPosition( pt );
				}
			}
		}
	}


	return MS::kSuccess;
}

void vertSnapDeformer::initVertMapping(MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix, unsigned int mIndex)
{
	//make poly mesh function set object:
	MDataHandle meshAttrHandle = data.inputValue( driver_mesh  );
	MObject meshMobj = meshAttrHandle.asMesh();
	MItMeshVertex vertIter( meshMobj );
	vertIter.reset();
	int count = iter.count();

	MArrayDataHandle vertMapOutArrayData = data.outputArrayValue( vert_map );

	MArrayDataBuilder vertMapOutArrayBuilder(vert_map, count);
	MPointArray allPts;
	allPts.clear();

	int i=0;
	//first initialize all mappings to -1, and also store a buffer pt array to search through:
	for( ; !iter.isDone(); iter.next() )
	{
		MDataHandle initIndexDataHnd = vertMapOutArrayBuilder.addElement( i );
		int negIndex = -1;

		initIndexDataHnd.setInt( negIndex );
		initIndexDataHnd.setClean();


		allPts.append( iter.position() * localToWorldMatrix );
		i++;
	}

	vertMapOutArrayData.set(vertMapOutArrayBuilder);

	for ( ; !vertIter.isDone(); vertIter.next() )
	{
		MPoint driver_pt = vertIter.position( MSpace::kWorld );
		int closest_pt_index = getClosestPt( driver_pt, allPts );

		//save the closest point mapping to snap verts to each other here:
		MDataHandle snapDataHnd = vertMapOutArrayBuilder.addElement( closest_pt_index );
		snapDataHnd.setInt( vertIter.index() );

		snapDataHnd.setClean();
	}

	vertMapOutArrayData.set( vertMapOutArrayBuilder );

	MPlug setInitMode(thisMObject(), initialized_data);
	setInitMode.setShort(2);

	iter.reset(); //important, reset the geom iterator so it starts from zero again

}

//this is really a brute force linear closest pt function,
//definately nothing fancy here (returns the pt index, not the point):
int vertSnapDeformer::getClosestPt( const MPoint& pt, const MPointArray& points )
{
	int ptIndex =0;
	double currentDistance = 9e99;
	double furthestDistanceSoFar = 9e99;

	for(unsigned int i=0; i < points.length(); i++ )
	{
		currentDistance = pt.distanceTo( points[i] );
		if( currentDistance < furthestDistanceSoFar )
		{
			ptIndex = i;
			furthestDistanceSoFar = currentDistance;
		}
	}

	return ptIndex;
}

void* vertSnapDeformer::creator()
{
	return new vertSnapDeformer();
}

MStatus vertSnapDeformer::initialize()	
{
	MFnNumericAttribute numericAttr;
	MFnTypedAttribute polyMeshAttr;
	MFnEnumAttribute enumAttr;

	driver_mesh = polyMeshAttr.create( "vertSnapInput", "vsnpin", MFnData::kMesh );
 	polyMeshAttr.setStorable(false);
	polyMeshAttr.setConnectable(true);
	addAttribute(driver_mesh);
	attributeAffects(driver_mesh, outputGeom);

	initialized_data = enumAttr.create( "initialize", "inl" );
	enumAttr.addField(	"Off", 0);
	enumAttr.addField(	"Re-Set Bind", 1);
	enumAttr.addField(	"Bound", 2);
	enumAttr.setKeyable(true);
	enumAttr.setStorable(true);
	enumAttr.setReadable(true);
	enumAttr.setWritable(true);
	enumAttr.setDefault(0);
	addAttribute( initialized_data );
	attributeAffects( initialized_data, outputGeom );

	vert_map = numericAttr.create( "vtxIndexMap", "vtximp", MFnNumericData::kLong );
	numericAttr.setKeyable(false);
	numericAttr.setArray(true);
	numericAttr.setStorable(true);
	numericAttr.setReadable(true);
	numericAttr.setWritable(true);
	addAttribute( vert_map );
	attributeAffects( vert_map, outputGeom  );

	// Make the deformer weights paintable
	MGlobal::executeCommand( "makePaintable -attrType multiFloat -sm deformer blendNode weights;" );

	return MS::kSuccess;
}

