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

#include "math.h"

#include "hrGeneralMuscleNode.h"

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>

#include <maya/MFnIntArrayData.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MFnDoubleArrayData.h>
#include <maya/MFnVectorArrayData.h>

#include <maya/MGlobal.h>
#include <maya/MFnNurbsSurface.h>
#include <maya/MFnNurbsSurfaceData.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnNurbsCurveData.h>

#include <maya/MMatrix.h>


MTypeId     hrGeneralMuscle::id( 0x00127 );

MObject		hrGeneralMuscle::calculateVolume;
MObject		hrGeneralMuscle::connectionSurface;
MObject		hrGeneralMuscle::connectionU;
MObject		hrGeneralMuscle::connectionV;
MObject		hrGeneralMuscle::connectionUp;
MObject		hrGeneralMuscle::connectionFlip;
MObject		hrGeneralMuscle::connectionPt;

MObject		hrGeneralMuscle::originVectorX;
MObject		hrGeneralMuscle::originVectorY;
MObject		hrGeneralMuscle::originVectorZ;
MObject		hrGeneralMuscle::originVectorPt;

MObject		hrGeneralMuscle::insertionVectorX;
MObject		hrGeneralMuscle::insertionVectorY;
MObject		hrGeneralMuscle::insertionVectorZ;
MObject		hrGeneralMuscle::insertionVectorPt;

MObject		hrGeneralMuscle::originVectorLock;
MObject		hrGeneralMuscle::insertionVectorLock;
MObject		hrGeneralMuscle::restHeightO;
MObject		hrGeneralMuscle::restHeightOv;
MObject		hrGeneralMuscle::restWidthOv;
MObject		hrGeneralMuscle::restHeightIv;
MObject		hrGeneralMuscle::restWidthIv;
MObject		hrGeneralMuscle::restHeightI;

MObject		hrGeneralMuscle::muscleLength;
MObject		hrGeneralMuscle::internalMuscleHeights;
MObject		hrGeneralMuscle::internalMuscleWidths;
MObject		hrGeneralMuscle::internalMuscleLength;
MObject		hrGeneralMuscle::internalInitialVolumes;
MObject		hrGeneralMuscle::internalMusclePositions;
MObject		hrGeneralMuscle::internalMuscleXsections;
MObject		hrGeneralMuscle::internalMuscleCurve;
MObject		hrGeneralMuscle::internalVPoints;
MObject		hrGeneralMuscle::internalWhichUp;
MObject		hrGeneralMuscle::internalMuscleLocks;
MObject		hrGeneralMuscle::muscleSurface;    

hrGeneralMuscle::hrGeneralMuscle() {}
hrGeneralMuscle::~hrGeneralMuscle() {}

MStatus hrGeneralMuscle::compute( const MPlug& plug, MDataBlock& data )
{
	if( plug == muscleSurface )
	{
		computeMuscleSurface(plug, data );
	}
	else if( plug == internalMuscleCurve )
	{
		computeMuscleCurve(plug, data );
	}
	else if ( plug == internalMuscleHeights )
	{
		computeMuscleHeights(plug, data );
	}
	else if ( plug == internalMuscleWidths )
	{
		computeMuscleWidths(plug, data );
	}
	else if ( plug == internalMuscleLength )
	{
		computeMuscleLength(plug, data );
	}
	else if ( plug == internalMusclePositions )
	{
		computeMusclePositions(plug, data );
	}
	else if ( plug == internalVPoints )
	{
		computeVPoints(plug, data );
	}
	else if ( plug == internalWhichUp )
	{
		computeWhichUp(plug, data );
	}
	else if ( plug == internalMuscleLocks )
	{
		computeMuscleLocks(plug, data );
	}
	else if ( plug == muscleLength )
	{
		computeContinuousMuscleLength(plug, data );
	}
	else
	{
		return MStatus::kUnknownParameter;
	}
	return MStatus::kSuccess;
}

void hrGeneralMuscle::computeMuscleSurface( const MPlug& plug, MDataBlock& data )
{
	bool vol = false;
	MPoint curCurveCV;
	MPoint newPt;
	MPointArray muscleMidPts;
	MPointArray surfaceCVs;
	MPointArray allCurveCVs;
	MDoubleArray uKnots;
	//MDoubleArray vKnots;
	MDoubleArray mHeights;
	MDoubleArray mWidths;
	MObject mObj;
	MVectorArray upVectors;
	MIntArray whichUps;
	MIntArray muscleLock;

	MVector o1Up;
	MVector o2Up;
	MVector i1Up;
	MVector i2Up;

	MPointArray adjustedCVsforRest;
	adjustedCVsforRest.setLength(44);

	MMatrix xform1;
	MMatrix xform2;
	MMatrix xform;

	double divisor = 1.0;
	double lfactor = 1.0;



	// GET ALL INPUT VALUES
	MDataHandle calcVolDataHnd = data.inputValue( calculateVolume );
	vol = calcVolDataHnd.asBool();	

	// get internal curve
	MDataHandle muscleCurveHnd = data.inputValue( internalMuscleCurve );
	mObj = muscleCurveHnd.asNurbsCurve();
	MFnNurbsCurve muscleCurveFn( mObj );

	// get knotsV for muscle surface
	muscleCurveFn.getKnots( uKnots );

	// get midPt positions into array
	MDataHandle musclePointPosHnd = data.inputValue( internalMusclePositions );
	MObject mObjPts = musclePointPosHnd.data();
	MFnPointArrayData pData( mObjPts );
	muscleMidPts = pData.array();


	// get muscle heights
	MDataHandle muscleHeightsHnd = data.inputValue( internalMuscleHeights );
	MObject mObjH = muscleHeightsHnd.data();
	MFnDoubleArrayData hData( mObjH );
	mHeights = hData.array();



    // get muscle widths
	MDataHandle muscleWidthsHnd = data.inputValue( internalMuscleWidths );
	MObject mObjW = muscleWidthsHnd.data();
	MFnDoubleArrayData wData( mObjW );
	mWidths = wData.array();



	// get muscle ups
	MDataHandle muscleVectorHnd = data.inputValue( internalVPoints );
	MObject mObjV = muscleVectorHnd.data();
	MFnVectorArrayData vData( mObjV );
	upVectors = vData.array();


	MDataHandle muscleUpsHnd = data.inputValue( internalWhichUp );
	MObject mObjWU = muscleUpsHnd.data();
	MFnIntArrayData wuData( mObjWU );
	whichUps = wuData.array();

	o1Up = upVectors[ (whichUps[0] * 4) + 0 ];
	o2Up = upVectors[ (whichUps[1] * 4) + 1 ];
	i1Up = upVectors[ (whichUps[2] * 4) + 2 ];
	i2Up = upVectors[ (whichUps[3] * 4) + 3 ];



	MDataHandle muscleLocksHnd = data.inputValue( internalMuscleLocks );
	MObject mObjML = muscleLocksHnd.data();
	MFnIntArrayData mlData( mObjML );
	muscleLock = mlData.array();

	MDataHandle restLengthHnd = data.inputValue( internalMuscleLength );
	double restLength = restLengthHnd.asDouble();

	if(vol)
	{
		divisor = muscleCurveFn.length();
		lfactor = sqrt( restLength / divisor );
	}

	////////////////////////////////////////////////////////////////////////
	// -=DO IT!=-

	int numXsections = 4;
	int numKnots = 13;
	MPoint adjustFix;
	int j = 0;
	int i = 0;
	int x = 0;
	int howMany = 0;
	MVector aVec;
	MVector bVec;
	MVector cVec;
	MVector opVec;
	double rH = 0.0;
	double rW = 0.0;

	MPointArray muscleXsectionPts;
	muscleXsectionPts.clear();
	muscleXsectionPts.setLength(4);

	muscleXsectionPts.set( muscleMidPts[0], 0 );
	muscleXsectionPts.set( muscleMidPts[1], 1 );
	muscleXsectionPts.set( muscleMidPts[3], 2 );
	muscleXsectionPts.set( muscleMidPts[4], 3 );

	MPointArray endPts;
	getEndPointPositions( data, endPts );

	adjustedCVsforRest.clear();


	for( int xSection=0; xSection < numXsections; xSection++ )
	{
		////////////////////////////////////////////////////
		//  CREATE U CVs

		allCurveCVs.clear();

		MPoint curCurveCV0( -0.424779, 0.000000, -1.025506, 1.0 );
		allCurveCVs.append( curCurveCV0 );

		MPoint curCurveCV1( 0.424779, 0.000000, -1.025506, 1.0 );
		allCurveCVs.append( curCurveCV1 );

		MPoint curCurveCV2( 1.025506, 0.000000, -0.424779, 1.0 );
		allCurveCVs.append( curCurveCV2 );

		MPoint curCurveCV3( 1.025506, 0.000000, 0.424779, 1.0 );
		allCurveCVs.append( curCurveCV3 );

		MPoint curCurveCV4( 0.424779, 0.000000, 1.025506, 1.0 );
		allCurveCVs.append( curCurveCV4 );

		MPoint curCurveCV5( -0.424779, 0.000000, 1.025506, 1.0 );
		allCurveCVs.append( curCurveCV5 );

		MPoint curCurveCV6( -1.025506, 0.000000, 0.424779, 1.0 );
		allCurveCVs.append( curCurveCV6 );

		MPoint curCurveCV7( -1.025506, 0.000000, -0.424779, 1.0 );
		allCurveCVs.append( curCurveCV7 );

		MPoint curCurveCV8( -0.424779, 0.000000, -1.025506, 1.0 );
		allCurveCVs.append( curCurveCV8 );

		MPoint curCurveCV9( 0.424779, 0.000000, -1.025506, 1.0 );
		allCurveCVs.append( curCurveCV9 );

		MPoint curCurveCV10( 1.025506, 0.000000, -0.424779, 1.0 );
		allCurveCVs.append( curCurveCV10 );

		////////////////////////////////////////////////////////////
		// Rotations for spans

		MVector upVec;
		MVector difVec;
		MVector outVec;
		MVector mVec;
		if( xSection == 0 || xSection == 1)
		{
			upVec = o1Up + o2Up;
			upVec.normalize();
			difVec = endPts[1] - endPts[0];
			difVec.normalize();
			outVec = upVec ^ difVec;
			outVec.normalize();

			bVec = difVec;

			MVector tmpVec( muscleXsectionPts[xSection] );
			MVector tmpEndVec1( endPts[0] );
			MVector tmpEndVec2( endPts[1] );

			if (xSection == 0)
			{
				cVec = (((outVec + tmpVec) - tmpEndVec1) + ((outVec + tmpVec) - tmpEndVec2)) / 2;
			}
			else if (xSection == 1)
			{
				if( muscleLock[ 0 ] == 0 )
				{
					cVec = muscleXsectionPts[0] - muscleXsectionPts[3];
				}
				else
				{
					MVector tmpVec2( muscleXsectionPts[xSection-1] );
					cVec = (((outVec+tmpVec2) - tmpEndVec1) + ((outVec+tmpVec2) - tmpEndVec2)) / 2;
				}				
			}			

			aVec = bVec ^ cVec;
			aVec.normalize();
			bVec = cVec ^ aVec;
			bVec.normalize();
		}

		else if(xSection == 3 || xSection == 2)
		{
			MVector tmpEndVec1( endPts[2] );
			MVector tmpEndVec2( endPts[3] );
			MVector tmpVec( muscleXsectionPts[xSection] );

			upVec = i1Up + i2Up;
			upVec.normalize();
			difVec = endPts[3] - endPts[2];
			difVec = endPts[3] - endPts[2];
			difVec.normalize();

			if (xSection == 3)
			{
				outVec =  ((difVec ^ upVec) * -1.0);
			}
			else if (xSection == 2)
			{
				outVec =  ( upVec ^ difVec);
			}			

			outVec.normalize();

			bVec = difVec;
			if (xSection == 3)
			{
				cVec = (((outVec+tmpVec) - tmpEndVec1) + ((outVec+tmpVec) - tmpEndVec2)) / 2;
			}
			else if (xSection == 2)
			{
				if( muscleLock[ 1 ] == 0 )
				{
					cVec = muscleXsectionPts[0] - muscleXsectionPts[3];
				}
				else
				{
					MVector tmpVec2( muscleXsectionPts[xSection+1] );
					cVec = (((outVec+tmpVec2) - tmpEndVec1) + ((outVec+tmpVec2) - tmpEndVec2)) / 2;
				}
			}
			aVec = (bVec ^ cVec);
			aVec.normalize();
			bVec = (cVec ^ aVec);
			bVec.normalize();
		}
			


		MVector vPts;
		MVector vectorPt;
		vPts.x = muscleXsectionPts[xSection].x;
		vPts.y = muscleXsectionPts[xSection].y;
		vPts.z = muscleXsectionPts[xSection].z;

		vectorPt = outVec + vPts;



		rW = mWidths[xSection];
		rH = mHeights[xSection];

		if(vol)
		{
			rW *= lfactor / 1.0;
			rH *= lfactor;
		}


		MPoint curXcurvePoint;

		for(int i=0; i < 11; i++ )
		{
			MPoint curXsectionPt = muscleXsectionPts[xSection];
			curXcurvePoint = allCurveCVs[i];

			//MMatrix xform1;
			xform1.setToIdentity();

			double val = rH * -1.0;
			xform1[0][0] = val;

			val = 0.0;
			xform1[0][1] = val;

			val = 0.0;
			xform1[0][2] = val;

			val = 0.0;
			xform1[1][0] = val;

			val = 0.0;
			xform1[1][1] = val;

			val = 1.0;
			xform1[1][2] = val;

			val = 0.0;
			xform1[2][0] = val;

			val = rW;
			xform1[2][1] = val;

			val = 0.0;
			xform1[2][2] = val;

			//MMatrix xform2;
			xform2.setToIdentity();

			xform2[0][0] =  aVec.x;
			xform2[0][1] =  aVec.y;
			xform2[0][2] =  aVec.z;
			xform2[1][0] =  bVec.x;
			xform2[1][1] =  bVec.y;
			xform2[1][2] =  bVec.z;
			xform2[2][0] =  cVec.x;
			xform2[2][1] =  cVec.y;
			xform2[2][2] =  cVec.z;
			xform2[3][0] = curXsectionPt.x;
			xform2[3][1] = curXsectionPt.y;
			xform2[3][2] = curXsectionPt.z;

			xform = xform1 * xform2;

			newPt = allCurveCVs[i] * xform;
			newPt.w = 1.0;

			adjustedCVsforRest.append(newPt);
		}
	}

	MDoubleArray vKnots;
	vKnots.clear();

	vKnots.append( -2.000000 );
	vKnots.append( -1.000000 );
	vKnots.append( 0.000000 );
	vKnots.append( 1.000000 );
	vKnots.append( 2.000000 );
	vKnots.append( 3.000000 );
	vKnots.append( 4.000000 );
	vKnots.append( 5.000000 );
	vKnots.append( 6.000000 );
	vKnots.append( 7.000000 );
	vKnots.append( 8.000000 );
	vKnots.append( 9.000000 );
	vKnots.append( 10.000000 );

	MFnNurbsSurfaceData sData;
	MObject mSurfObj = sData.create();
	MFnNurbsSurface mSurfFn;

	mSurfFn.create(adjustedCVsforRest, uKnots, vKnots, 3, 3, MFnNurbsSurface::kOpen, MFnNurbsSurface::kPeriodic, false, mSurfObj );

	MDataHandle muscleSurfaceOutHnd = data.outputValue( muscleSurface );

	muscleSurfaceOutHnd.setMObject( mSurfObj );
	muscleSurfaceOutHnd.setClean();
	
}

void hrGeneralMuscle::computeMuscleHeights( const MPlug& plug, MDataBlock& data )
{
	double oRH = 0.0;
	double ovRH = 0.0;
	double ivRH = 0.0;
	double iRH = 0.0;
	MDoubleArray restHeights;
	bool vol = false;
	MObject obj;

	MDataHandle calcVolDataHnd = data.inputValue( calculateVolume );
	vol = calcVolDataHnd.asBool();

	MDataHandle OriginRHDataHnd = data.inputValue( restHeightO );
	oRH = OriginRHDataHnd.asDouble();

	MDataHandle OriginVRHDataHnd = data.inputValue( restHeightOv );
	ovRH = OriginVRHDataHnd.asDouble();

	MDataHandle InsertVRHDataHnd = data.inputValue( restHeightIv );
	ivRH = InsertVRHDataHnd.asDouble();

	MDataHandle InsertRHDataHnd = data.inputValue( restHeightI );
	iRH = InsertRHDataHnd.asDouble();	

	restHeights.clear();
	restHeights.setLength(4);
	restHeights.set(oRH, 0);
	restHeights.set(ovRH, 1);
	restHeights.set(ivRH, 2);
	restHeights.set(iRH, 3);

	MDataHandle restHeightsDataHnd = data.outputValue( internalMuscleHeights );

	MFnDoubleArrayData dData;
	obj = dData.create( restHeights );
	restHeightsDataHnd.setMObject( obj );
	restHeightsDataHnd.setClean();
}

void hrGeneralMuscle::computeMuscleWidths( const MPlug& plug, MDataBlock& data )
{
	double ovRW = 0.0;
	double ivRW = 0.0;
	MDoubleArray restWidths;
	MPoint oPt1;
	MPoint oPt2;
	MPoint iPt1;
	MPoint iPt2;
	bool vol = false;

	MDataHandle calcVolDataHnd = data.inputValue( calculateVolume );
	vol = calcVolDataHnd.asBool();
	MPointArray endPts;
	getEndPointPositions( data, endPts );

	MDataHandle OriginVRWDataHnd = data.inputValue( restWidthOv );
	ovRW = OriginVRWDataHnd.asDouble();

	MDataHandle InsertVRWDataHnd = data.inputValue( restWidthIv );
	ivRW = InsertVRWDataHnd.asDouble();	

	double halfOriginDist = endPts[0].distanceTo(endPts[1])/ 2;
	double halfInsertDist = endPts[2].distanceTo(endPts[3])/ 2;

	restWidths.clear();
	restWidths.setLength(4);
	restWidths.set(halfOriginDist, 0);
	restWidths.set(ovRW, 1);
	restWidths.set(ivRW, 2);
	restWidths.set(halfInsertDist, 3);

	MDataHandle restWidthsDataHnd = data.outputValue( internalMuscleWidths );

	MFnDoubleArrayData dData;
	MObject obj = dData.create( restWidths );
	restWidthsDataHnd.setMObject( obj );
	restWidthsDataHnd.setClean();

}

void hrGeneralMuscle::computeMuscleLength( const MPlug& plug, MDataBlock& data )
{
	bool vol = false;

	MDataHandle calcVolDataHnd = data.inputValue( calculateVolume ) ;
	vol = calcVolDataHnd.asBool();

	if( vol )
	{
		data.setClean(internalMuscleLength);
	}
	else
	{
		MDataHandle curveLengthHnd = data.inputValue( internalMuscleCurve );
		MObject curveObj = curveLengthHnd.asNurbsCurve();

		MFnNurbsCurve curveFn( curveObj );

		double length = curveFn.length();
		MDataHandle curveLengthOUTHnd = data.outputValue( internalMuscleLength );

		curveLengthOUTHnd.setDouble(length);
		curveLengthOUTHnd.setClean();
	}

}

void hrGeneralMuscle::computeContinuousMuscleLength( const MPlug& plug, MDataBlock& data )
{
	MDataHandle curveLengthHnd = data.inputValue( internalMuscleCurve );
	MObject curveObj = curveLengthHnd.asNurbsCurve();

	MFnNurbsCurve curveFn( curveObj );
	double length = curveFn.length();

	MDataHandle curveLengthcOutHnd = data.outputValue( muscleLength );

	curveLengthcOutHnd.set(length);
	data.setClean(muscleLength);
}

void hrGeneralMuscle::computeMusclePositions( const MPlug& plug, MDataBlock& data )
{
	MPointArray xSectionPositions;
	MPoint oPt;
	MPoint iPt;

	MPointArray endPts;
	getEndPointPositions( data, endPts );


	xSectionPositions.setLength(5);

	// set midPoints via given points

	oPt.x = (endPts[0].x + endPts[1].x) / 2;
	oPt.y = (endPts[0].y + endPts[1].y) / 2;
	oPt.z = (endPts[0].z + endPts[1].z) / 2;
	oPt.w = 1.0;

	iPt.x = (endPts[2].x + endPts[3].x) / 2;
	iPt.y = (endPts[2].y + endPts[3].y) / 2;
	iPt.z = (endPts[2].z + endPts[3].z) / 2;
	iPt.w = 1.0;

	MPoint centerPt;
	MPoint ovCenter;
	MPoint ivCenter;
	MPoint tmpOV;
	MPoint tmpIV;
	centerPt.x = (oPt.x + iPt.x) / 2;
	centerPt.y = (oPt.y + iPt.y) / 2;
	centerPt.z = (oPt.z + iPt.z) / 2;
	centerPt.w = 1.0;

	ovCenter.x = ( oPt.x + centerPt.x ) / 2;
	ovCenter.y = ( oPt.y + centerPt.y ) / 2;
	ovCenter.z = ( oPt.z + centerPt.z ) / 2;

	ivCenter.x = ( iPt.x + centerPt.x ) / 2;
	ivCenter.y = ( iPt.y + centerPt.y ) / 2;
	ivCenter.z = ( iPt.z + centerPt.z ) / 2;


	MDataHandle OriginVXDataHnd = data.inputValue( originVectorX );
	double ovX = OriginVXDataHnd.asDouble();	
	MDataHandle OriginVYDataHnd = data.inputValue( originVectorY );
	double ovY = OriginVYDataHnd.asDouble();	
	MDataHandle OriginVZDataHnd = data.inputValue( originVectorZ );
	double ovZ = OriginVZDataHnd.asDouble();

	MDataHandle InsertionVXDataHnd = data.inputValue( insertionVectorX );
	double ivX = InsertionVXDataHnd.asDouble();		
	MDataHandle InsertionVYDataHnd = data.inputValue( insertionVectorY );
	double ivY = InsertionVYDataHnd.asDouble();	
	MDataHandle InsertionVZDataHnd = data.inputValue( insertionVectorZ );
	double ivZ = (-1 * InsertionVZDataHnd.asDouble());

	MVector o1Up;
	MVector o2Up;
	MVector i1Up;
	MVector i2Up;
	// get ups

	MDataHandle muscleVectorHnd = data.inputValue( internalVPoints );
	MObject mObjV = muscleVectorHnd.data();
	MFnVectorArrayData vData( mObjV );
	MVectorArray upVectors = vData.array();


	o1Up = upVectors[ 0 ];
	o2Up = upVectors[ 1 ];
	i1Up = upVectors[ 2 ];
	i2Up = upVectors[ 3 ];

	MVector OupVec;
	MVector IupVec;
	MVector OdifVec;
	MVector IdifVec;
	MVector OoutVec;
	MVector IoutVec;

	OupVec = o1Up + o2Up;
	OupVec.normalize();
	IupVec = i1Up + i2Up;
	IupVec.normalize();

	OdifVec = endPts[1] - endPts[0];
	OdifVec.normalize();
	IdifVec = endPts[3] - endPts[2];
	IdifVec.normalize();

	OoutVec = OupVec ^ OdifVec;
	OoutVec.normalize();
	IoutVec = IupVec ^ IdifVec;
	IoutVec.normalize();

	MDataHandle muscleLocksHnd = data.inputValue( internalMuscleLocks );
	MObject mObjML = muscleLocksHnd.data();
	MFnIntArrayData mlData( mObjML );
	MIntArray muscleLock = mlData.array();

	if( muscleLock[ 0 ] == 0 )
	{
		tmpOV = ovCenter+((OdifVec * ovX)+(OupVec*ovY)+(OoutVec*ovZ));
	}

	else
	{
		tmpOV = oPt + ((OdifVec * ovX)+(OupVec*ovY)+(OoutVec*ovZ));
	}


	if( muscleLock[ 1 ] == 0 )
	{
		tmpIV = ivCenter+((IdifVec * ivX)+(IupVec*ivY)+(IoutVec*ivZ));
	}
	else
	{
		tmpIV = iPt + ((IdifVec * ivX)+(IupVec*ivY)+(IoutVec*ivZ));
	}


	xSectionPositions.set( oPt, 0 );
	xSectionPositions.set( tmpOV, 1 );
	xSectionPositions.set( centerPt, 2 );
	xSectionPositions.set( tmpIV, 3 );
	xSectionPositions.set( iPt, 4 );

	MDataHandle musclePositionsDataHnd = data.outputValue( internalMusclePositions );

	MFnPointArrayData dData;
 	MObject obj = dData.create(xSectionPositions);
	musclePositionsDataHnd.setMObject(obj);
	musclePositionsDataHnd.setClean();
}

void hrGeneralMuscle::getEndPointPositions( MDataBlock& data, MPointArray& returnPointArray )
{
    // get ups
	MVectorArray mUps;
	MVectorArray mUs;
	MVectorArray mVs;
	MIntArray whichUp;
	getInputData( data, returnPointArray, mUps, mUs, mVs, whichUp);
}

void hrGeneralMuscle::computeVPoints( const MPlug& plug, MDataBlock& data )
{
	MPointArray mPointPositions;
	MVectorArray mUps;
	MVectorArray mUs;
	MVectorArray mVs;
	MIntArray whichUp;
	getInputData( data, mPointPositions, mUps, mUs, mVs, whichUp);

	MVectorArray vectorsArray;
	vectorsArray.clear();
	vectorsArray.append(mUps[0]);
	vectorsArray.append(mUps[1]);
	vectorsArray.append(mUps[2]);
	vectorsArray.append(mUps[3]);
	vectorsArray.append(mUs[0]);
	vectorsArray.append(mUs[1]);
	vectorsArray.append(mUs[2]);
	vectorsArray.append(mUs[3]);
	vectorsArray.append(mVs[0]);
	vectorsArray.append(mVs[1]);
	vectorsArray.append(mVs[2]);
	vectorsArray.append(mVs[3]);

	MDataHandle internalVPointsHnd = data.outputValue( internalVPoints );

	MFnVectorArrayData vData;
	MObject obj = vData.create(vectorsArray);
	internalVPointsHnd.setMObject(obj);

	internalVPointsHnd.setClean();
}

void hrGeneralMuscle::computeMuscleCurve( const MPlug& plug, MDataBlock& data )
{
	MFnNurbsCurve curveFn;
	MPointArray cvs;
	MPointArray tmpPositions;
	MDoubleArray knots;
	MFnNurbsCurveData curveData;

	MDataHandle musclePositionsDataHnd = data.inputValue( internalMusclePositions );

	MObject cvArray = musclePositionsDataHnd.data();
	MFnPointArrayData mPositions( cvArray );
	tmpPositions = mPositions.array();


	cvs.setLength(4);
	cvs.set( tmpPositions[0], 0 );
	cvs.set( tmpPositions[1], 1 );
	cvs.set( tmpPositions[3], 2 );
	cvs.set( tmpPositions[4], 3 );

	MObject obj = curveData.create();
	knots.clear();
	int j = 0;
	double sum = 1.0;

	int numKnots = 6 ;

	for(int i=0; i<numKnots; i++)
	{
		if (i < 3)
		{
			knots.append( 0.0 );
		}
		else
		{
			knots.append( sum );
		}
	}


	curveFn.create(cvs, knots, 3, MFnNurbsCurve::kOpen, false, false, obj );

	MDataHandle lengthCurveHnd = data.outputValue( internalMuscleCurve );
	lengthCurveHnd.setMObject(obj);

	lengthCurveHnd.setClean();
}

void hrGeneralMuscle::getInputData( MDataBlock& data, MPointArray& mPointPositions, MVectorArray& mUps, MVectorArray& mUs,MVectorArray& mVs,MIntArray& whichUp)
{
	mPointPositions.clear();
	mUps.clear();
	mUs.clear();
	mVs.clear();
	whichUp.clear();

	MVector tempVec;
	MVector tempVecU;
	MVector tempVecV;


	// get input connections
	MArrayDataHandle connectionPtHnd = data.inputArrayValue( connectionPt );
	int num = connectionPtHnd.elementCount();

	for (int curElem=0; curElem < num; curElem++ )
	{
		connectionPtHnd.jumpToElement( curElem );
		MDataHandle inputPt = connectionPtHnd.inputValue();

		MDataHandle inputSurf = inputPt.child( connectionSurface );
		MObject MObj = inputSurf.asNurbsSurface();
		MFnNurbsSurface surfFn( MObj );

		MDataHandle inputU = inputPt.child( connectionU );
		double Uparam = inputU.asDouble();
		MDataHandle inputV = inputPt.child( connectionV );
		double Vparam = inputV.asDouble();
		MDataHandle inputUp = inputPt.child( connectionUp );
		int up = inputUp.asInt();
		whichUp.append( up );
		MDataHandle inputFlip = inputPt.child( connectionFlip );
		bool flip = inputFlip.asBool();

		MPoint tempPos;
		surfFn.getPointAtParam( Uparam, Vparam, tempPos, MSpace::kWorld );
		mPointPositions.append(tempPos);

		tempVec = surfFn.normal( Uparam, Vparam, MSpace::kWorld );

		if( flip )
		{
			tempVec = (tempVec * -1.0);
		}		
		tempVec.normalize();
		mUps.append(tempVec);

		surfFn.getTangents( Uparam, Vparam, tempVecU, tempVecV, MSpace::kWorld );
		if( flip )
		{
			tempVecU = (tempVecU * -1.0);
			tempVecV = (tempVecV * -1.0);
		}
		

		tempVecU.normalize();
		tempVecV.normalize();

		mUs.append(tempVecU);
		mVs.append(tempVecV);
	}

}

void hrGeneralMuscle::computeWhichUp( const MPlug& plug, MDataBlock& data )
{
	MPointArray mPointPositions;
	MVectorArray mUps;
	MVectorArray mUs;
	MVectorArray mVs;
	MIntArray whichUp;
	getInputData( data, mPointPositions, mUps, mUs, mVs, whichUp);

	MDataHandle internalWhichUpHnd = data.outputValue( internalWhichUp );

	MFnIntArrayData wUData;
	MObject obj = wUData.create(whichUp);
	internalWhichUpHnd.setMObject(obj);

	internalWhichUpHnd.setClean();
}

void hrGeneralMuscle::computeMuscleLocks( const MPlug& plug, MDataBlock& data )
{
	MIntArray muscleLocks;
	muscleLocks.clear();
	muscleLocks.setLength(2);

	MDataHandle originMLockHnd = data.inputValue( originVectorLock );
	int oL = originMLockHnd.asInt();

	MDataHandle insertionMLockHnd = data.inputValue( insertionVectorLock );
	int iL = insertionMLockHnd.asInt();

	muscleLocks.set( oL, 0 );
	muscleLocks.set( iL, 1 );

	MDataHandle internalMuscleLocksHnd = data.outputValue( internalMuscleLocks );

	MFnIntArrayData mLData;
	MObject obj = mLData.create(muscleLocks);
	internalMuscleLocksHnd.setMObject(obj);

	internalMuscleLocksHnd.setClean();
}

void* hrGeneralMuscle::creator()
{
	return new hrGeneralMuscle();
}

MStatus hrGeneralMuscle::initialize()	
{
	MStatus   status;

	MFnNumericAttribute nAttr;
	MFnTypedAttribute tAttr;
	MFnCompoundAttribute cAttr;
	MFnUnitAttribute uAttr;
	MFnEnumAttribute eAttr;


	calculateVolume = nAttr.create( "calculateVolume", "vol", MFnNumericData::kBoolean, 0.0);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);

	connectionSurface = tAttr.create( "connectionSurface", "conS", MFnData::kNurbsSurface );
	tAttr.setStorable( true );
	tAttr.setHidden( true );
	tAttr.setKeyable( false );
	tAttr.setConnectable( true );
	tAttr.setReadable( false );
	tAttr.setWritable( true );
	tAttr.setArray( false );

	connectionU = nAttr.create( "connectionU", "conU", MFnNumericData::kDouble, 0.0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( false );
	nAttr.setConnectable( false );
	nAttr.setReadable( false );
	nAttr.setHidden( true );

	connectionV = nAttr.create( "connectionV", "conV", MFnNumericData::kDouble, 0.0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( false );
	nAttr.setConnectable( false );
	nAttr.setReadable( false );
	nAttr.setHidden( true );

	connectionUp = nAttr.create( "connectionUp", "conUp", MFnNumericData::kInt, 0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( false );
	nAttr.setConnectable( false );
	nAttr.setReadable( false );
	nAttr.setHidden( true );

	connectionFlip = nAttr.create( "connectionFlip", "conF", MFnNumericData::kBoolean, 0.0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( false );
	nAttr.setConnectable( false );
	nAttr.setReadable( false );
	nAttr.setHidden( true );

	connectionPt = cAttr.create( "connectionPt", "conP" );
	cAttr.setStorable( true );
	cAttr.setKeyable( false );
	cAttr.setConnectable( false );
	cAttr.setReadable( false );
	cAttr.setHidden( true );
	cAttr.setArray( true );

	cAttr.addChild( connectionSurface );
	cAttr.addChild( connectionU );
	cAttr.addChild( connectionV );
	cAttr.addChild( connectionUp );
	cAttr.addChild( connectionFlip );

	////////////////////////////////////////////////
	originVectorX = uAttr.create( "originVectorX", "ovx", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);

	originVectorY = uAttr.create( "originVectorY", "ovy", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);	

	originVectorZ = uAttr.create( "originVectorZ", "ovz", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);

	originVectorPt = cAttr.create( "originVectorPt", "ov");
	cAttr.setStorable(true);
	cAttr.setKeyable(true);

	cAttr.addChild(originVectorX);
	cAttr.addChild(originVectorY);
	cAttr.addChild(originVectorZ);

	insertionVectorX = uAttr.create( "insertionVectorX", "ivx", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);

	insertionVectorY = uAttr.create( "insertionVectorY", "ivy", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);	

	insertionVectorZ = uAttr.create( "insertionVectorZ", "ivz", MFnUnitAttribute::kDistance, 0.0);
	uAttr.setStorable(true);
	uAttr.setKeyable(true);

	insertionVectorPt = cAttr.create( "insertionVectorPt", "iv");
	cAttr.setStorable(true);
	cAttr.setKeyable(true);

	cAttr.addChild(insertionVectorX);
	cAttr.addChild(insertionVectorY);
	cAttr.addChild(insertionVectorZ);

	originVectorLock = nAttr.create( "originVectorLock", "oLk", MFnNumericData::kBoolean, 0.0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( true );
	nAttr.setConnectable( true );
	nAttr.setReadable( true );
	nAttr.setHidden( false );

	insertionVectorLock = nAttr.create( "insertionVectorLock", "iLk", MFnNumericData::kBoolean, 0.0 );
	nAttr.setStorable( true );
	nAttr.setKeyable( true );
	nAttr.setConnectable( true );
	nAttr.setReadable( true );
	nAttr.setHidden( false );

	////////////////////////////////////////////////
	restHeightO = uAttr.create( "restHeightO", "rHo", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	////////////////////////////////////////////////
	restHeightOv = uAttr.create( "restHeightOv", "rHov", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	restWidthOv = uAttr.create( "restWidthOv", "rWov", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	////////////////////////////////////////////////
	restHeightIv = uAttr.create( "restHeightIv", "rHiv", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	restWidthIv = uAttr.create( "restWidthIv", "rWiv", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	////////////////////////////////////////////////
	restHeightI = uAttr.create( "restHeightI", "rHi", MFnUnitAttribute::kDistance, 1.0 );
	uAttr.setStorable( true );
	uAttr.setMin( 0.0 );
	uAttr.setKeyable( true );

	////////////////////////////////////////////////
	muscleLength = uAttr.create( "muscleLength", "mL", MFnUnitAttribute::kDistance, 0.0 );
	uAttr.setStorable( false );
	uAttr.setConnectable( true );
	uAttr.setReadable( true );
	uAttr.setWritable( false );

	////////////////////////////////////////////////
	internalMuscleHeights = tAttr.create( "internalMuscleHeights", "iRh", MFnData::kDoubleArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMuscleWidths = tAttr.create( "internalMuscleWidths", "iRw", MFnData::kDoubleArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMuscleLength = uAttr.create( "internalMuscleLength", "iRl", MFnUnitAttribute::kDistance, 0.0 );
	uAttr.setStorable( true );
	uAttr.setHidden( true );
	uAttr.setConnectable( false );
	uAttr.setReadable( false );
	uAttr.setWritable( true );

	internalInitialVolumes = tAttr.create( "internalInitialVolumes", "iIv", MFnData::kDoubleArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMusclePositions	= tAttr.create( "internalMusclePositions", "iMp", MFnData::kPointArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMuscleXsections	= tAttr.create( "internalMuscleXsections", "iXs", MFnData::kNurbsCurve  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMuscleCurve	= tAttr.create( "internalMuscleCurve", "icv", MFnData::kNurbsCurve  );
	tAttr.setStorable( false );


	internalVPoints = tAttr.create( "internalVPoints", "iVp", MFnData::kVectorArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalWhichUp = tAttr.create( "internalWhichUp", "iwu", MFnData::kIntArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	internalMuscleLocks = tAttr.create( "internalMuscleLocks", "iml", MFnData::kIntArray  );
	tAttr.setStorable( false );
	tAttr.setHidden( true );
	tAttr.setConnectable( false );
	tAttr.setReadable( false );
	tAttr.setWritable( false );

	////////////////////////////////////////////////
	muscleSurface = tAttr.create( "muscleSurface", "ms", MFnData::kNurbsSurface  );
	tAttr.setWritable(false);
	tAttr.setStorable(false);

	////////////////////////////////////////////////////////////////////////////
	status = addAttribute( calculateVolume );

	status = addAttribute( connectionPt );


	status = addAttribute( originVectorPt );

	status = addAttribute( originVectorLock );

	status = addAttribute( insertionVectorPt );

	status = addAttribute( insertionVectorLock );

	status = addAttribute( restHeightO );

	status = addAttribute( restHeightOv );

	status = addAttribute( restWidthOv );

	status = addAttribute( restHeightIv );

	status = addAttribute( restWidthIv );

	status = addAttribute( restHeightI );

	status = addAttribute( muscleLength );

	status = addAttribute( internalMuscleHeights );

	status = addAttribute( internalMuscleWidths );

	status = addAttribute( internalMuscleLength );

	status = addAttribute( internalInitialVolumes );

	status = addAttribute( internalWhichUp );

	status = addAttribute( internalMuscleLocks );

	status = addAttribute( internalMusclePositions );

	status = addAttribute( internalMuscleXsections );


	status = addAttribute( internalVPoints );


	status = addAttribute( internalMuscleCurve );


	status = addAttribute( muscleSurface );



	///////////////////////////////////////////////////////


	attributeAffects( calculateVolume, muscleSurface );
	attributeAffects( connectionPt, muscleSurface );
	attributeAffects( connectionSurface, muscleSurface );
	attributeAffects( connectionU, muscleSurface );
	attributeAffects( connectionV, muscleSurface );
	attributeAffects( connectionUp, muscleSurface );
	attributeAffects( connectionFlip, muscleSurface );
	attributeAffects( originVectorPt, muscleSurface );
	attributeAffects( insertionVectorPt, muscleSurface );
	attributeAffects( restHeightO, muscleSurface );
	attributeAffects( restHeightOv, muscleSurface );
	attributeAffects( restWidthOv, muscleSurface );
	attributeAffects( restHeightIv, muscleSurface );
	attributeAffects( restWidthIv, muscleSurface );
	attributeAffects( restHeightI, muscleSurface );
	attributeAffects( originVectorLock, muscleSurface );
	attributeAffects( insertionVectorLock, muscleSurface );

    ///////////////////////////////////////////////


	attributeAffects( restHeightO, internalMuscleHeights );
	attributeAffects( restHeightOv, internalMuscleHeights );
	attributeAffects( restHeightIv, internalMuscleHeights );
	attributeAffects( restHeightI, internalMuscleHeights );
	attributeAffects( calculateVolume, internalMuscleHeights );

	attributeAffects( restWidthOv, internalMuscleWidths );
	attributeAffects( restWidthIv, internalMuscleWidths );
	attributeAffects( calculateVolume, internalMuscleWidths );
	attributeAffects( connectionPt, internalMuscleWidths );



	///////////////////////////////////////////////


	attributeAffects( connectionPt, internalMuscleLength );
	attributeAffects( connectionSurface, internalMuscleLength );
	attributeAffects( connectionU, internalMuscleLength );
	attributeAffects( connectionV, internalMuscleLength );
	attributeAffects( connectionUp, internalMuscleLength );
	attributeAffects( connectionFlip, internalMuscleLength );
	attributeAffects( calculateVolume, internalMuscleLength );
	attributeAffects( originVectorPt, internalMuscleLength );
	attributeAffects( insertionVectorPt, internalMuscleLength );


	///////////////////////////////////////////////


	attributeAffects( originVectorPt, internalMusclePositions );
	attributeAffects( connectionPt, internalMusclePositions );
	attributeAffects( connectionSurface, internalMusclePositions );
	attributeAffects( connectionU, internalMusclePositions );
	attributeAffects( connectionV, internalMusclePositions );
	attributeAffects( connectionUp, internalMusclePositions );
	attributeAffects( connectionFlip, internalMusclePositions );
	attributeAffects( insertionVectorPt, internalMusclePositions );
	attributeAffects( originVectorLock, internalMusclePositions );
	attributeAffects( insertionVectorLock, internalMusclePositions );


	///////////////////////////////////////////////


	attributeAffects( connectionUp, internalWhichUp );


	///////////////////////////////////////////////


	attributeAffects( connectionPt, internalMuscleCurve );
	attributeAffects( connectionPt, internalMuscleCurve );
	attributeAffects( connectionSurface, internalMuscleCurve );
	attributeAffects( connectionU, internalMuscleCurve );
	attributeAffects( connectionV, internalMuscleCurve );
	attributeAffects( connectionUp, internalMuscleCurve );
	attributeAffects( connectionFlip, internalMuscleCurve );
	attributeAffects( insertionVectorPt, internalMuscleCurve );
	attributeAffects( originVectorLock, internalMuscleCurve );
	attributeAffects( insertionVectorLock, internalMuscleCurve );


	///////////////////////////////////////////////


	attributeAffects( connectionPt, internalVPoints );
	attributeAffects( connectionSurface, internalVPoints );
	attributeAffects( connectionU, internalVPoints );
	attributeAffects( connectionV, internalVPoints );
	attributeAffects( connectionUp, internalVPoints );
	attributeAffects( connectionFlip, internalVPoints );


	///////////////////////////////////////////////


	attributeAffects( originVectorLock, internalMuscleLocks );
	attributeAffects( insertionVectorLock, internalMuscleLocks );


	///////////////////////////////////////////////


	attributeAffects( connectionPt, muscleLength );
	attributeAffects( connectionSurface, muscleLength );
	attributeAffects( connectionU, muscleLength );
	attributeAffects( connectionV, muscleLength );
	attributeAffects( connectionUp, muscleLength );
	attributeAffects( connectionFlip, muscleLength );
	attributeAffects( originVectorPt, muscleLength );
	attributeAffects( insertionVectorPt, muscleLength );


	return MS::kSuccess;

}

