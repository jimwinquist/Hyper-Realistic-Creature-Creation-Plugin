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

#ifndef _hrGeneralMuscleNode
#define _hrGeneralMuscleNode

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MTypeId.h> 

#include <maya/MIntArray.h>
#include <maya/MPointArray.h>
#include <maya/MVectorArray.h>

 
class hrGeneralMuscle : public MPxNode
{
public:
						hrGeneralMuscle();
	virtual				~hrGeneralMuscle(); 

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

	static  void*		creator();
	static  MStatus		initialize();

public:

	static	MTypeId		id;
	static  MObject		calculateVolume;
	static  MObject		connectionSurface;
	static  MObject		connectionU;
	static  MObject		connectionV;
	static  MObject		connectionUp;
	static  MObject		connectionFlip;
	static  MObject		connectionPt;

	static  MObject		originVectorX;
	static  MObject		originVectorY;
	static  MObject		originVectorZ;
	static  MObject		originVectorPt;

	static  MObject		insertionVectorX;
	static  MObject		insertionVectorY;
	static  MObject		insertionVectorZ;
	static  MObject		insertionVectorPt;

	static  MObject		originVectorLock;
	static  MObject		insertionVectorLock;
	static  MObject		restHeightO;
	static  MObject		restHeightOv;
	static  MObject		restWidthOv;
	static  MObject		restHeightIv;
	static  MObject		restWidthIv;
	static  MObject		restHeightI;

	static  MObject		muscleLength;
	static  MObject		internalMuscleHeights;
	static  MObject		internalMuscleWidths;
	static  MObject		internalMuscleLength;
	static  MObject		internalInitialVolumes;
	static  MObject		internalMusclePositions;
	static  MObject		internalMuscleXsections;
	static  MObject		internalMuscleCurve;
	static  MObject		internalVPoints;
	static  MObject		internalWhichUp;
	static  MObject		internalMuscleLocks;
	static  MObject		muscleSurface;

public:
	
	void computeMuscleSurface( const MPlug& plug, MDataBlock& data );
	void computeMuscleHeights( const MPlug& plug, MDataBlock& data );
	void computeMuscleWidths( const MPlug& plug, MDataBlock& data );
	void computeMuscleLength( const MPlug& plug, MDataBlock& data );

	void computeContinuousMuscleLength( const MPlug& plug, MDataBlock& data );
	void computeMusclePositions( const MPlug& plug, MDataBlock& data );
	void getEndPointPositions( MDataBlock& data, MPointArray& returnPointArray );
	void computeVPoints( const MPlug& plug, MDataBlock& data );
	void computeMuscleCurve( const MPlug& plug, MDataBlock& data );

	void getInputData( MDataBlock& data, 
		MPointArray& mPointPositions, 
		MVectorArray& mUps, 
		MVectorArray& mUs,
		MVectorArray& mVs,
		MIntArray& whichUp);

	void computeWhichUp( const MPlug& plug, MDataBlock& data );
	void computeMuscleLocks( const MPlug& plug, MDataBlock& data );

};

#endif
