##############################################################################
'''
hrGeneralMuscle.py
Paul Thuriot
copywrite 2009

Python plugin for:
HYPER REAL 2 book - 2009

NOTE: There is a significant speed hit when using a python plugin versus a compiled C plugin.  The benefit is that this python plugin should work on any OS (Win/ Mac/ Linux) and Maya version (8.5+).

NOTE: Tested on Win (32/ 64) and Linux for Maya 8.5, 2008, +

References:

Anatomy Based Modeling of the Human Musculature, Ferdi Scheepers, Richard E. Parent. Wayne E. Carlson and Stephen F. May; SIGGRAPH '97
'''
##############################################################################

import math, sys

import maya.cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx


kPluginNodeTypeName = "hrGeneralMuscle"

# CHANGE THIS ID AS NEEDED
hrGeneralMuscleID = OpenMaya.MTypeId( 0x00127 )


#==================================================
# Node definition
class hrGeneralMuscle( OpenMayaMPx.MPxNode ):
	#----------------------------------------
	# class variables
	calculateVolume = OpenMaya.MObject()
	
	connectionSurface = OpenMaya.MObject()
	connectionU = OpenMaya.MObject()
	connectionV = OpenMaya.MObject()
	connectionUp = OpenMaya.MObject()
	connectionFlip = OpenMaya.MObject()
	connectionPt = OpenMaya.MObject()
	
	originVectorX = OpenMaya.MObject()
	originVectorY = OpenMaya.MObject()
	originVectorZ = OpenMaya.MObject()
	originVectorPt = OpenMaya.MObject()
	
	insertionVectorX = OpenMaya.MObject()
	insertionVectorY = OpenMaya.MObject()
	insertionVectorZ = OpenMaya.MObject()
	insertionVectorPt = OpenMaya.MObject()
	
	muscleLength = OpenMaya.MObject()
	
	restHeightO = OpenMaya.MObject()
	restHeightOv = OpenMaya.MObject()
	restWidthOv = OpenMaya.MObject()
	restHeightIv = OpenMaya.MObject()
	restWidthIv = OpenMaya.MObject()
	restHeightI = OpenMaya.MObject()
	
	internalMuscleHeights = OpenMaya.MObject()
	internalMuscleWidths = OpenMaya.MObject()
	internalMuscleLength = OpenMaya.MObject()
	internalInitialVolumes = OpenMaya.MObject()
	
	internalMusclePositions = OpenMaya.MObject()
	internalMuscleXsections = OpenMaya.MObject()
	internalMuscleCurve = OpenMaya.MObject()
	internalWhichUp = OpenMaya.MObject()
	
	originVectorLock = OpenMaya.MObject()
	insertionVectorLock = OpenMaya.MObject()
	internalMuscleLocks = OpenMaya.MObject()
	
	internalVPoints = OpenMaya.MObject()
	
	muscleSurface = OpenMaya.MObject()
	
	
	
	
	
	
	
	#==================================================
	# constructor
	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
	
	
	
	
	
	
	
	#==================================================
	# compute
	def compute( self, plug, dataBlock ):
		
		if( plug == self.muscleSurface ):
			self.computeMuscleSurface(plug, dataBlock )
			
		elif( plug == self.internalMuscleCurve ):
			self.computeMuscleCurve(plug, dataBlock )
			
		elif ( plug == self.internalMuscleHeights ):
			self.computeMuscleHeights(plug, dataBlock )
			
		elif ( plug == self.internalMuscleWidths ):
			self.computeMuscleWidths(plug, dataBlock )
			
		elif ( plug == self.internalMuscleLength ):
			self.computeMuscleLength(plug, dataBlock )
			
		elif ( plug == self.internalMusclePositions ):
			self.computeMusclePositions(plug, dataBlock )
			
		elif ( plug == self.internalVPoints ):
			self.computeVPoints(plug, dataBlock )
			
		elif ( plug == self.internalWhichUp ):
			self.computeWhichUp(plug, dataBlock )
			
		elif ( plug == self.internalMuscleLocks ):
			self.computeMuscleLocks(plug, dataBlock )
			
		elif ( plug == self.muscleLength ):
			self.computeContinuousMuscleLength(plug, dataBlock )
			
		else:
			return OpenMaya.kUnknownParameter
	
	#==================================================
	def computeMuscleSurface( self, plug, dataBlock ):
		vol = False
		curCurveCV = OpenMaya.MPoint()
		newPt  = OpenMaya.MPoint()
		muscleMidPts= OpenMaya.MPointArray()
		surfaceCVs = OpenMaya.MPointArray()
		allCurveCVs = OpenMaya.MPointArray()
		uKnots = OpenMaya.MDoubleArray()
		vKnots = OpenMaya.MDoubleArray()
		mHeights = OpenMaya.MDoubleArray()
		mWidths = OpenMaya.MDoubleArray()
		mObj = OpenMaya.MObject()
		upVectors = OpenMaya.MVectorArray()
		whichUps = OpenMaya.MIntArray()
		muscleLock = OpenMaya.MIntArray()
		
		o1Up = OpenMaya.MVector()
		o2Up = OpenMaya.MVector()
		i1Up = OpenMaya.MVector()
		i2Up = OpenMaya.MVector()
		
		adjustedCVsforRest = OpenMaya.MPointArray()
		adjustedCVsforRest.setLength(44)
		
		xform1 = OpenMaya.MMatrix()
		xform2 = OpenMaya.MMatrix()
		xform = OpenMaya.MMatrix()
		
		divisor = 1.0
		lfactor = 1.0
		
		
		
		# GET ALL INPUT VALUES
		calcVolDataHnd = dataBlock.inputValue( self.calculateVolume )
		vol = calcVolDataHnd.asBool()	
	
		# get internal curve
		muscleCurveHnd = dataBlock.inputValue( self.internalMuscleCurve )
		mObj = muscleCurveHnd.asNurbsCurve()
		muscleCurveFn = OpenMaya.MFnNurbsCurve( mObj )
		
		# get knotsV for muscle surface
		muscleCurveFn.getKnots( uKnots )
		
		# get midPt positions into array
		musclePointPosHnd = dataBlock.inputValue( self.internalMusclePositions )
		mObjPts = musclePointPosHnd.data()
		pData = OpenMaya.MFnPointArrayData( mObjPts )
		muscleMidPts = pData.array()
		
		
		# get muscle heights
		muscleHeightsHnd = dataBlock.inputValue( self.internalMuscleHeights )
		mObjH = muscleHeightsHnd.data()
		hData = OpenMaya.MFnDoubleArrayData( mObjH )
		mHeights = hData.array()
		
		
		
		# get muscle widths
		muscleWidthsHnd = dataBlock.inputValue( self.internalMuscleWidths )
		mObjW = muscleWidthsHnd.data()
		wData = OpenMaya.MFnDoubleArrayData( mObjW )
		mWidths = wData.array()
		
		
		
		# get muscle ups
		muscleVectorHnd = dataBlock.inputValue( self.internalVPoints )
		mObjV = muscleVectorHnd.data()
		vData = OpenMaya.MFnVectorArrayData( mObjV )
	
		upVectors = vData.array()
		
		
		muscleUpsHnd = dataBlock.inputValue( self.internalWhichUp )
		mObjWU = muscleUpsHnd.data()
		wuData = OpenMaya.MFnIntArrayData( mObjWU )
		whichUps = wuData.array()
		
		o1Up = upVectors[ (whichUps[0] * 4) + 0 ]
		o2Up = upVectors[ (whichUps[1] * 4) + 1 ]
		i1Up = upVectors[ (whichUps[2] * 4) + 2 ]
		i2Up = upVectors[ (whichUps[3] * 4) + 3 ]
	
	
	
		muscleLocksHnd = dataBlock.inputValue( self.internalMuscleLocks )
		mObjML = muscleLocksHnd.data()
		mlData = OpenMaya.MFnIntArrayData( mObjML )
		muscleLock = mlData.array()
		
		restLengthHnd = dataBlock.inputValue( self.internalMuscleLength )
		restLength = restLengthHnd.asDouble()
	
		if(vol):
			divisor = muscleCurveFn.length()
			lfactor = math.sqrt( restLength / divisor )
	
		#======================================================================
		# -=DO IT!=-
	
		numXsections = 4
		numKnots = 13
		adjustFix = OpenMaya.MPoint()
		j = 0
		i = 0
		x = 0
		howMany = 0
		aVec = OpenMaya.MVector()
		bVec = OpenMaya.MVector()
		cVec = OpenMaya.MVector()
		opVec = OpenMaya.MVector()
		rH = 0.0
		rW = 0.0
	
		muscleXsectionPts = OpenMaya.MPointArray()
		muscleXsectionPts.clear()
		muscleXsectionPts.setLength(4)
		
		muscleXsectionPts.set( muscleMidPts[0], 0 )
		muscleXsectionPts.set( muscleMidPts[1], 1 )
		muscleXsectionPts.set( muscleMidPts[3], 2 )
		muscleXsectionPts.set( muscleMidPts[4], 3 )
		
		endPts = OpenMaya.MPointArray()
		self.getEndPointPositions( dataBlock, endPts )
		
		adjustedCVsforRest.clear()
	
	
		for xSection in range( 0, numXsections ):
			#------------------------------------------------------
			#  CREATE U CVs
		
			allCurveCVs.clear()	
				
			curCurveCV0 = OpenMaya.MPoint( -0.424779, 0.000000, -1.025506, 1.0 )
			allCurveCVs.append( curCurveCV0 )
			curCurveCV1 = OpenMaya.MPoint( 0.424779, 0.000000, -1.025506, 1.0 )
			allCurveCVs.append( curCurveCV1 )
			curCurveCV2 = OpenMaya.MPoint( 1.025506, 0.000000, -0.424779, 1.0 )
			allCurveCVs.append( curCurveCV2 )
			curCurveCV3 = OpenMaya.MPoint( 1.025506, 0.000000, 0.424779, 1.0 )
			allCurveCVs.append( curCurveCV3 )
			curCurveCV4 = OpenMaya.MPoint( 0.424779, 0.000000, 1.025506, 1.0 )
			allCurveCVs.append( curCurveCV4 )
			curCurveCV5 = OpenMaya.MPoint( -0.424779, 0.000000, 1.025506, 1.0 )
			allCurveCVs.append( curCurveCV5 )
			curCurveCV6 = OpenMaya.MPoint( -1.025506, 0.000000, 0.424779, 1.0 )
			allCurveCVs.append( curCurveCV6 )
			curCurveCV7 = OpenMaya.MPoint( -1.025506, 0.000000, -0.424779, 1.0 )
			allCurveCVs.append( curCurveCV7 )
			curCurveCV8 = OpenMaya.MPoint( -0.424779, 0.000000, -1.025506, 1.0 )
			allCurveCVs.append( curCurveCV8 )
			curCurveCV9 = OpenMaya.MPoint( 0.424779, 0.000000, -1.025506, 1.0 )
			allCurveCVs.append( curCurveCV9 )
			curCurveCV10 = OpenMaya.MPoint( 1.025506, 0.000000, -0.424779, 1.0 )
			allCurveCVs.append( curCurveCV10 )
		
			#------------------------------------------------------
			# Rotations for spans
			
			upVec = OpenMaya.MVector()
			difVec = OpenMaya.MVector()
			outVec = OpenMaya.MVector()
			mVec = OpenMaya.MVector()
			if( xSection == 0 or xSection == 1):
				
				upVec = o1Up + o2Up
				upVec.normalize()
				difVec = endPts[1] - endPts[0]
				difVec.normalize()
				outVec = upVec ^ difVec
				outVec.normalize()
				
				bVec = difVec 
				
				tmpVec = OpenMaya.MVector( muscleXsectionPts[xSection] )
				tmpEndVec1 = OpenMaya.MVector( endPts[0] )
				tmpEndVec2 = OpenMaya.MVector( endPts[1] )
				
				if (xSection == 0):
					cVec = (((outVec + tmpVec) - tmpEndVec1) + ((outVec + tmpVec) - tmpEndVec2)) / 2
				elif (xSection == 1):
					if( muscleLock[ 0 ] == 0 ):
						cVec = muscleXsectionPts[0] - muscleXsectionPts[3]
					else:
						tmpVec2 = OpenMaya.MVector( muscleXsectionPts[xSection-1] )
				
						cVec = (((outVec+tmpVec2) - tmpEndVec1) + ((outVec+tmpVec2) - tmpEndVec2)) / 2
				
				aVec = bVec ^ cVec
				aVec.normalize()
				bVec = cVec ^ aVec
				bVec.normalize()
			
	
			elif(xSection == 3 or xSection == 2):
				tmpEndVec1 = OpenMaya.MVector( endPts[2] )
				tmpEndVec2 = OpenMaya.MVector( endPts[3] )
				
				upVec = i1Up + i2Up
				upVec.normalize()
				difVec = endPts[3] - endPts[2]
				difVec = endPts[3] - endPts[2]
				difVec.normalize()
				if (xSection == 3):
					outVec =  ((difVec ^ upVec) * -1.0)
				elif (xSection == 2):
					outVec =  ( upVec ^ difVec)
				
				outVec.normalize()
				
				bVec = difVec 
				if (xSection == 3):
					cVec = (((outVec+tmpVec) - tmpEndVec1) + ((outVec+tmpVec) - tmpEndVec2)) / 2
				elif (xSection == 2):
					if( muscleLock[ 1 ] == 0 ):
						cVec = muscleXsectionPts[0] - muscleXsectionPts[3]
					else:
						tmpVec2 = OpenMaya.MVector( muscleXsectionPts[xSection+1] )
				
						cVec = (((outVec+tmpVec2) - tmpEndVec1) + ((outVec+tmpVec2) - tmpEndVec2)) / 2
				
				aVec = (bVec ^ cVec)
				aVec.normalize()
				bVec = (cVec ^ aVec)
				bVec.normalize()	
			
	
			vPts = OpenMaya.MVector()
			vectorPt = OpenMaya.MVector()
			vPts.x = muscleXsectionPts[xSection].x
			vPts.y = muscleXsectionPts[xSection].y
			vPts.z = muscleXsectionPts[xSection].z
			
			vectorPt = outVec + vPts
			
			
			
			rW = mWidths[xSection]
			rH = mHeights[xSection]

			if(vol):
				rW *= lfactor / 1.0
				rH *= lfactor

			curXcurvePoint = OpenMaya.MPoint()
			
			for i in range( 0, 11 ):
				curXsectionPt = muscleXsectionPts[xSection]
				curXcurvePoint = allCurveCVs[i]
				
				xform1 = OpenMaya.MMatrix()
				xform1.setToIdentity()
				
				val = rH * -1.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[0], 0, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[0], 1, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[0], 2, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[1], 0, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[1], 1, val)
				
				val = 1.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[1], 2, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[2], 0, val)
				
				val = rW
				OpenMaya.MScriptUtil.setDoubleArray(xform1[2], 1, val)
				
				val = 0.0
				OpenMaya.MScriptUtil.setDoubleArray(xform1[2], 2, val)
				
				xform2 = OpenMaya.MMatrix()
				xform2.setToIdentity()
				
				OpenMaya.MScriptUtil.setDoubleArray(xform2[0], 0, aVec.x)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[0], 1, aVec.y)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[0], 2, aVec.z)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[1], 0, bVec.x)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[1], 1, bVec.y)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[1], 2, bVec.z)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[2], 0, cVec.x)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[2], 1, cVec.y)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[2], 2, cVec.z)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[3], 0, curXsectionPt.x)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[3], 1, curXsectionPt.y)
				OpenMaya.MScriptUtil.setDoubleArray(xform2[3], 2, curXsectionPt.z)
				
				xform = xform1 * xform2
				
				newPt = allCurveCVs[i] * xform
				newPt.w = 1.0
				
				adjustedCVsforRest.append(newPt)
				
				
				
		vKnots = OpenMaya.MDoubleArray()
		vKnots.clear()
		
		vKnots.append( -2.000000 )
		vKnots.append( -1.000000 )
		vKnots.append( 0.000000 )
		vKnots.append( 1.000000 )
		vKnots.append( 2.000000 )
		vKnots.append( 3.000000 )
		vKnots.append( 4.000000 )
		vKnots.append( 5.000000 )
		vKnots.append( 6.000000 )
		vKnots.append( 7.000000 )
		vKnots.append( 8.000000 )
		vKnots.append( 9.000000 )
		vKnots.append( 10.000000 )
	
		sData = OpenMaya.MFnNurbsSurfaceData()
		mSurfObj = sData.create()
		mSurfFn = OpenMaya.MFnNurbsSurface()
			
		mSurfFn.create(adjustedCVsforRest, uKnots, vKnots, 3, 3, OpenMaya.MFnNurbsSurface.kOpen, OpenMaya.MFnNurbsSurface.kPeriodic, False, mSurfObj )
		
		muscleSurfaceOutHnd = dataBlock.outputValue( self.muscleSurface )
		
		muscleSurfaceOutHnd.setMObject( mSurfObj )
		muscleSurfaceOutHnd.setClean()
	
	
	
	def computeMuscleHeights( self, plug, data ):
		oRH = 0.0
		ovRH = 0.0
		ivRH = 0.0
		iRH = 0.0
		restHeights = OpenMaya.MDoubleArray()
		vol = False
		obj = OpenMaya.MObject()
		
		calcVolDataHnd = data.inputValue( self.calculateVolume )
		vol = calcVolDataHnd.asBool()	
		
		OriginRHDataHnd = data.inputValue( self.restHeightO )
		oRH = OriginRHDataHnd.asDouble()		
		
		OriginVRHDataHnd = data.inputValue( self.restHeightOv )
		ovRH = OriginVRHDataHnd.asDouble()		
	
		InsertVRHDataHnd = data.inputValue( self.restHeightIv )
		ivRH = InsertVRHDataHnd.asDouble()		
	
		InsertRHDataHnd = data.inputValue( self.restHeightI )
		iRH = InsertRHDataHnd.asDouble()		
		
		restHeights.clear()
		restHeights.setLength(4)
		restHeights.set(oRH, 0)
		restHeights.set(ovRH, 1)
		restHeights.set(ivRH, 2)
		restHeights.set(iRH, 3)
	
		restHeightsDataHnd = data.outputValue( self.internalMuscleHeights )
		
		dData = OpenMaya.MFnDoubleArrayData()
		obj = dData.create( restHeights )
		restHeightsDataHnd.setMObject( obj )
		restHeightsDataHnd.setClean()
		
		
		
		
	def computeMuscleWidths( self, plug, data ):
		ovRW = 0.0
		ivRW = 0.0
		restWidths = OpenMaya.MDoubleArray()
		oPt1 = OpenMaya.MPoint()
		oPt2 = OpenMaya.MPoint()
		iPt1 = OpenMaya.MPoint()
		iPt2 = OpenMaya.MPoint()
		vol = False
	
		calcVolDataHnd = data.inputValue( self.calculateVolume )
		vol = calcVolDataHnd.asBool()	
		endPts = OpenMaya.MPointArray()
		self.getEndPointPositions( data, endPts )
		
		OriginVRWDataHnd = data.inputValue( self.restWidthOv )
		ovRW = OriginVRWDataHnd.asDouble()		
	
		InsertVRWDataHnd = data.inputValue( self.restWidthIv )
		ivRW = InsertVRWDataHnd.asDouble()		
			
		halfOriginDist = endPts[0].distanceTo(endPts[1])/ 2
		halfInsertDist = endPts[2].distanceTo(endPts[3])/ 2
		
		restWidths.clear()
		restWidths.setLength(4)
		restWidths.set(halfOriginDist, 0)
		restWidths.set(ovRW, 1)
		restWidths.set(ivRW, 2)
		restWidths.set(halfInsertDist, 3)
		
		restWidthsDataHnd = data.outputValue( self.internalMuscleWidths )
		
		dData = OpenMaya.MFnDoubleArrayData()
		obj = dData.create( restWidths )
		restWidthsDataHnd.setMObject( obj )
		restWidthsDataHnd.setClean()
		
	
	
	
	def computeMuscleLength( self, plug, data ):
		vol = False
	
		calcVolDataHnd = data.inputValue( self.calculateVolume ) 
		vol = calcVolDataHnd.asBool()	
	
		if( vol ):
			data.setClean(self.internalMuscleLength)
		
		else:
			curveLengthHnd = data.inputValue( self.internalMuscleCurve )
			curveObj = OpenMaya.MObject() 
			curveObj = curveLengthHnd.asNurbsCurve()
			
			curveFn = OpenMaya.MFnNurbsCurve( curveObj )
			
			length = curveFn.length()
			curveLengthOUTHnd = data.outputValue( self.internalMuscleLength )
			
			curveLengthOUTHnd.setDouble(length)
			curveLengthOUTHnd.setClean()
	
	
	
	
	def computeContinuousMuscleLength( self, plug, data ):
		curveLengthHnd = data.inputValue( self.internalMuscleCurve )
		curveObj = OpenMaya.MObject()
		curveObj = curveLengthHnd.asNurbsCurve()
		
		curveFn = OpenMaya.MFnNurbsCurve( curveObj )
		length = curveFn.length()
	
		curveLengthcOutHnd = data.outputValue( self.muscleLength )
		
		curveLengthcOutHnd.set(length)
		data.setClean(muscleLength)
		
	
	def computeMusclePositions( self, plug, data ):
		xSectionPositions = OpenMaya.MPointArray()
		oPt = OpenMaya.MPoint()
		iPt = OpenMaya.MPoint()
	
		endPts = OpenMaya.MPointArray()
		self.getEndPointPositions( data, endPts )
		
		
		xSectionPositions.setLength(5)
	
		# set midPoints via given points
	
		oPt.x = (endPts[0].x + endPts[1].x) / 2
		oPt.y = (endPts[0].y + endPts[1].y) / 2
		oPt.z = (endPts[0].z + endPts[1].z) / 2
		oPt.w = 1.0
	
		iPt.x = (endPts[2].x + endPts[3].x) / 2
		iPt.y = (endPts[2].y + endPts[3].y) / 2
		iPt.z = (endPts[2].z + endPts[3].z) / 2
		iPt.w = 1.0
	
		centerPt = OpenMaya.MPoint()
		ovCenter = OpenMaya.MPoint()
		ivCenter = OpenMaya.MPoint()
		tmpOV = OpenMaya.MPoint()
		tmpIV = OpenMaya.MPoint()
		centerPt.x = (oPt.x + iPt.x) / 2
		centerPt.y = (oPt.y + iPt.y) / 2
		centerPt.z = (oPt.z + iPt.z) / 2
		centerPt.w = 1.0
	
		ovCenter.x = ( oPt.x + centerPt.x ) / 2
		ovCenter.y = ( oPt.y + centerPt.y ) / 2
		ovCenter.z = ( oPt.z + centerPt.z ) / 2
		
		ivCenter.x = ( iPt.x + centerPt.x ) / 2
		ivCenter.y = ( iPt.y + centerPt.y ) / 2
		ivCenter.z = ( iPt.z + centerPt.z ) / 2
		
	
		OriginVXDataHnd = data.inputValue( self.originVectorX )
		ovX = OriginVXDataHnd.asDouble()		
		OriginVYDataHnd = data.inputValue( self.originVectorY )
		ovY = OriginVYDataHnd.asDouble()	
		OriginVZDataHnd = data.inputValue( self.originVectorZ )
		ovZ = OriginVZDataHnd.asDouble()
	
		InsertionVXDataHnd = data.inputValue( self.insertionVectorX )
		ivX = InsertionVXDataHnd.asDouble()		
		InsertionVYDataHnd = data.inputValue( self.insertionVectorY )
		ivY = InsertionVYDataHnd.asDouble()	
		InsertionVZDataHnd = data.inputValue( self.insertionVectorZ )
		ivZ = (-1 * InsertionVZDataHnd.asDouble())
	
		o1Up = OpenMaya.MVector()
		o2Up = OpenMaya.MVector()
		i1Up = OpenMaya.MVector()
		i2Up = OpenMaya.MVector()
		# get ups
	
		muscleVectorHnd = data.inputValue( self.internalVPoints )
		mObjV = muscleVectorHnd.data()
		vData = OpenMaya.MFnVectorArrayData( mObjV )
		upVectors = vData.array()

	
		o1Up = upVectors[ 0 ]
		o2Up = upVectors[ 1 ]
		i1Up = upVectors[ 2 ]
		i2Up = upVectors[ 3 ]
	
		OupVec = OpenMaya.MVector()
		IupVec = OpenMaya.MVector()
		OdifVec = OpenMaya.MVector()
		IdifVec = OpenMaya.MVector()
		OoutVec = OpenMaya.MVector()
		IoutVec = OpenMaya.MVector()
		
		OupVec = o1Up + o2Up
		OupVec.normalize()
		IupVec = i1Up + i2Up
		IupVec.normalize()
		
		OdifVec = endPts[1] - endPts[0]
		OdifVec.normalize()
		IdifVec = endPts[3] - endPts[2]
		IdifVec.normalize()
		
		OoutVec = OupVec ^ OdifVec
		OoutVec.normalize()
		IoutVec = IupVec ^ IdifVec
		IoutVec.normalize()
	
		muscleLocksHnd = data.inputValue( self.internalMuscleLocks )
		mObjML = muscleLocksHnd.data()
		mlData = OpenMaya.MFnIntArrayData( mObjML )
		muscleLock = OpenMaya.MIntArray()
		muscleLock = mlData.array()
		
		if( muscleLock[ 0 ] == 0 ):
			tmpOV = ovCenter+((OdifVec * ovX)+(OupVec*ovY)+(OoutVec*ovZ))
		else:
			tmpOV = oPt + ((OdifVec * ovX)+(OupVec*ovY)+(OoutVec*ovZ))
		
		if( muscleLock[ 1 ] == 0 ):
			tmpIV = ivCenter+((IdifVec * ivX)+(IupVec*ivY)+(IoutVec*ivZ))
		else:
			tmpIV = iPt + ((IdifVec * ivX)+(IupVec*ivY)+(IoutVec*ivZ))
	
		xSectionPositions.set( oPt, 0 )
		xSectionPositions.set( tmpOV, 1 )
		xSectionPositions.set( centerPt, 2 )
		xSectionPositions.set( tmpIV, 3 )
		xSectionPositions.set( iPt, 4 )
	
		musclePositionsDataHnd = data.outputValue( self.internalMusclePositions )
		
		dData = OpenMaya.MFnPointArrayData()
		obj = dData.create(xSectionPositions)
		musclePositionsDataHnd.setMObject(obj)
		musclePositionsDataHnd.setClean()
	
	
	
	
	
	
	
	def getEndPointPositions( self, data, returnPointArray ):
		# get ups
		mUps = OpenMaya.MVectorArray()
		mUs = OpenMaya.MVectorArray()
		mVs = OpenMaya.MVectorArray()
		whichUp = OpenMaya.MIntArray()
		self.getInputData( data, returnPointArray, mUps, mUs, mVs, whichUp)
		
		
		
		
	def computeVPoints(self, plug, data):
		mPointPositions = OpenMaya.MPointArray()
		mUps = OpenMaya.MVectorArray()
		mUs = OpenMaya.MVectorArray()
		mVs = OpenMaya.MVectorArray()
		whichUp = OpenMaya.MIntArray()
		self.getInputData( data, mPointPositions, mUps, mUs, mVs, whichUp)
		
		vectorsArray = OpenMaya.MVectorArray()
		vectorsArray.clear()
		vectorsArray.append(mUps[0])
		vectorsArray.append(mUps[1])
		vectorsArray.append(mUps[2])
		vectorsArray.append(mUps[3])
		vectorsArray.append(mUs[0])
		vectorsArray.append(mUs[1])
		vectorsArray.append(mUs[2])
		vectorsArray.append(mUs[3])
		vectorsArray.append(mVs[0])
		vectorsArray.append(mVs[1])
		vectorsArray.append(mVs[2])
		vectorsArray.append(mVs[3])
		
		internalVPointsHnd = data.outputValue( self.internalVPoints )
		
		vData = OpenMaya.MFnVectorArrayData()
		obj = vData.create(vectorsArray)
		internalVPointsHnd.setMObject(obj)
		
		internalVPointsHnd.setClean()
	
	
	def computeMuscleCurve(self, plug, data):
		curveFn = OpenMaya.MFnNurbsCurve()
		cvs = OpenMaya.MPointArray()
		tmpPositions = OpenMaya.MPointArray()
		knots = OpenMaya.MDoubleArray()
		curveData = OpenMaya.MFnNurbsCurveData()
		
		musclePositionsDataHnd = data.inputValue( self.internalMusclePositions )
		
		cvArray = musclePositionsDataHnd.data()
		mPositions = OpenMaya.MFnPointArrayData( cvArray )
		tmpPositions = mPositions.array()
		
		
		
		
		cvs.setLength(4)
		cvs.set( tmpPositions[0], 0 )
		cvs.set( tmpPositions[1], 1 )
		cvs.set( tmpPositions[3], 2 )
		cvs.set( tmpPositions[4], 3 )
		
		obj = curveData.create()
		knots.clear()
		j = 0
		sum = 1.0
	
		numKnots = 6 
	
		for i in range (0, 3):
			knots.append( 0.0 )	
		for i in range( 3, numKnots ):
			knots.append( sum )
		
	
		curveFn.create(cvs, knots, 3, OpenMaya.MFnNurbsCurve.kOpen, False, False, obj )
		
		lengthCurveHnd = data.outputValue( self.internalMuscleCurve )
		lengthCurveHnd.setMObject(obj)
			
		lengthCurveHnd.setClean()
	
	
	def getInputData(self, data, mPointPositions, mUps, mUs, mVs, whichUp):
		mPointPositions.clear()
		mUps.clear()
		mUs.clear()
		mVs.clear()
		whichUp.clear()
	
		tempVec = OpenMaya.MVector()
		tempVecU = OpenMaya.MVector()
		tempVecV = OpenMaya.MVector()
	
	
		# get input connections
		connectionPtHnd = data.inputArrayValue( self.connectionPt )
		num = connectionPtHnd.elementCount()
		
		for curElem in range( 0, num ):
			connectionPtHnd.jumpToElement( curElem )
			inputPt = connectionPtHnd.inputValue()
			
			inputSurf = inputPt.child( self.connectionSurface )
			MObj = inputSurf.asNurbsSurface()
			surfFn = OpenMaya.MFnNurbsSurface( MObj )
	
			inputU = inputPt.child( self.connectionU )
			Uparam = inputU.asDouble()
			inputV = inputPt.child( self.connectionV )
			Vparam = inputV.asDouble()
			inputUp = inputPt.child( self.connectionUp )
			up = inputUp.asInt()
			whichUp.append( up )
			inputFlip = inputPt.child( self.connectionFlip )
			flip = inputFlip.asBool()
	
			tempPos = OpenMaya.MPoint()
			surfFn.getPointAtParam( Uparam, Vparam, tempPos, OpenMaya.MSpace.kWorld )
			mPointPositions.append(tempPos)
	
			tempVec = surfFn.normal( Uparam, Vparam, OpenMaya.MSpace.kWorld )
			
			if( flip ):
				tempVec = (tempVec * -1.0)
			tempVec.normalize()
			mUps.append(tempVec)
	
			surfFn.getTangents( Uparam, Vparam, tempVecU, tempVecV, OpenMaya.MSpace.kWorld )
			if( flip ):
				tempVecU = (tempVecU * -1.0)
				tempVecV = (tempVecV * -1.0)
			
			tempVecU.normalize()
			tempVecV.normalize()
	
			mUs.append(tempVecU)
			mVs.append(tempVecV)
	
	def computeWhichUp(self, plug, data):
		mPointPositions = OpenMaya.MPointArray()
		mUps = OpenMaya.MVectorArray()
		mUs = OpenMaya.MVectorArray()
		mVs = OpenMaya.MVectorArray()
		whichUp = OpenMaya.MIntArray()
		self.getInputData( data, mPointPositions, mUps, mUs, mVs, whichUp)
		
		internalWhichUpHnd = data.outputValue( self.internalWhichUp )
		
		wUData = OpenMaya.MFnIntArrayData()
		obj = wUData.create(whichUp)
		internalWhichUpHnd.setMObject(obj)
	
		internalWhichUpHnd.setClean()
	
	
	def computeMuscleLocks(self, plug, data):
		muscleLocks = OpenMaya.MIntArray()
		muscleLocks.clear()
		muscleLocks.setLength(2)
		
		originMLockHnd = data.inputValue( self.originVectorLock )
		oL = originMLockHnd.asInt()
	
		insertionMLockHnd = data.inputValue( self.insertionVectorLock )
		iL = insertionMLockHnd.asInt()
	
		muscleLocks.set( oL, 0 )
		muscleLocks.set( iL, 1 )
	
		internalMuscleLocksHnd = data.outputValue( self.internalMuscleLocks )
		
		mLData = OpenMaya.MFnIntArrayData()
		obj = mLData.create(muscleLocks)
		internalMuscleLocksHnd.setMObject(obj)
	
		internalMuscleLocksHnd.setClean()

	
	
	
	
	
	
	
#==================================================
# creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( hrGeneralMuscle() )
	

#==================================================
# initializer
def nodeInitializer():
	nAttr = OpenMaya.MFnNumericAttribute()
	tAttr = OpenMaya.MFnTypedAttribute()
	cAttr = OpenMaya.MFnCompoundAttribute()
	uAttr = OpenMaya.MFnUnitAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	
	
	hrGeneralMuscle.calculateVolume = nAttr.create( "calculateVolume", "vol", OpenMaya.MFnNumericData.kBoolean, 0.0)
	nAttr.setStorable(True)
	nAttr.setKeyable(True)

	hrGeneralMuscle.connectionSurface = tAttr.create( "connectionSurface", "conS", OpenMaya.MFnData.kNurbsSurface )
	tAttr.setStorable( True )
	tAttr.setHidden( True )
	tAttr.setKeyable( False )
	tAttr.setConnectable( True )
	tAttr.setReadable( False )
	tAttr.setWritable( True )
	tAttr.setArray( False )
	
	hrGeneralMuscle.connectionU = nAttr.create( "connectionU", "conU", OpenMaya.MFnNumericData.kDouble, 0.0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( False )
	nAttr.setConnectable( False )
	nAttr.setReadable( False )
	nAttr.setHidden( True )
	
	hrGeneralMuscle.connectionV = nAttr.create( "connectionV", "conV", OpenMaya.MFnNumericData.kDouble, 0.0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( False )
	nAttr.setConnectable( False )
	nAttr.setReadable( False )
	nAttr.setHidden( True )
	
	hrGeneralMuscle.connectionUp = nAttr.create( "connectionUp", "conUp", OpenMaya.MFnNumericData.kInt, 0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( False )
	nAttr.setConnectable( False )
	nAttr.setReadable( False )
	nAttr.setHidden( True )
	
	hrGeneralMuscle.connectionFlip = nAttr.create( "connectionFlip", "conF", OpenMaya.MFnNumericData.kBoolean, 0.0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( False )
	nAttr.setConnectable( False )
	nAttr.setReadable( False )
	nAttr.setHidden( True )
	
	hrGeneralMuscle.connectionPt = cAttr.create( "connectionPt", "conP" )
	cAttr.setStorable( True )
	cAttr.setKeyable( False )
	cAttr.setConnectable( False )
	cAttr.setReadable( False )
	cAttr.setHidden( True )
	cAttr.setArray( True )

	cAttr.addChild( hrGeneralMuscle.connectionSurface )
	cAttr.addChild( hrGeneralMuscle.connectionU )
	cAttr.addChild( hrGeneralMuscle.connectionV )
	cAttr.addChild( hrGeneralMuscle.connectionUp )
	cAttr.addChild( hrGeneralMuscle.connectionFlip )

	#---------------------------------------

	hrGeneralMuscle.originVectorX = uAttr.create( "originVectorX", "ovx", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)
	
	hrGeneralMuscle.originVectorY = uAttr.create( "originVectorY", "ovy", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)	
	
	hrGeneralMuscle.originVectorZ = uAttr.create( "originVectorZ", "ovz", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)

	hrGeneralMuscle.originVectorPt = cAttr.create( "originVectorPt", "ov")
	cAttr.setStorable(True)
	cAttr.setKeyable(True)

	cAttr.addChild(hrGeneralMuscle.originVectorX)
	cAttr.addChild(hrGeneralMuscle.originVectorY)
	cAttr.addChild(hrGeneralMuscle.originVectorZ)

	hrGeneralMuscle.insertionVectorX = uAttr.create( "insertionVectorX", "ivx", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)
	
	hrGeneralMuscle.insertionVectorY = uAttr.create( "insertionVectorY", "ivy", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)	
	
	hrGeneralMuscle.insertionVectorZ = uAttr.create( "insertionVectorZ", "ivz", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
	uAttr.setStorable(True)
	uAttr.setKeyable(True)

	hrGeneralMuscle.insertionVectorPt = cAttr.create( "insertionVectorPt", "iv")
	cAttr.setStorable(True)
	cAttr.setKeyable(True)

	cAttr.addChild(hrGeneralMuscle.insertionVectorX)
	cAttr.addChild(hrGeneralMuscle.insertionVectorY)
	cAttr.addChild(hrGeneralMuscle.insertionVectorZ)

	hrGeneralMuscle.originVectorLock = nAttr.create( "originVectorLock", "oLk", OpenMaya.MFnNumericData.kBoolean, 0.0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( True )
	nAttr.setConnectable( True )
	nAttr.setReadable( True )
	nAttr.setHidden( False )

	hrGeneralMuscle.insertionVectorLock = nAttr.create( "insertionVectorLock", "iLk", OpenMaya.MFnNumericData.kBoolean, 0.0 )
	nAttr.setStorable( True )
	nAttr.setKeyable( True )
	nAttr.setConnectable( True )
	nAttr.setReadable( True )
	nAttr.setHidden( False )

	#---------------------------------------
	
	hrGeneralMuscle.restHeightO = uAttr.create( "restHeightO", "rHo", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	#------------------------------

	hrGeneralMuscle.restHeightOv = uAttr.create( "restHeightOv", "rHov", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	hrGeneralMuscle.restWidthOv = uAttr.create( "restWidthOv", "rWov", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	#------------------------------

	hrGeneralMuscle.restHeightIv = uAttr.create( "restHeightIv", "rHiv", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	hrGeneralMuscle.restWidthIv = uAttr.create( "restWidthIv", "rWiv", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	#------------------------------

	hrGeneralMuscle.restHeightI = uAttr.create( "restHeightI", "rHi", OpenMaya.MFnUnitAttribute.kDistance, 1.0 )
	uAttr.setStorable( True )
	uAttr.setMin( 0.0 )
	uAttr.setKeyable( True )

	#------------------------------

	hrGeneralMuscle.muscleLength = uAttr.create( "muscleLength", "mL", OpenMaya.MFnUnitAttribute.kDistance, 0.0 )
	uAttr.setStorable( False )
	uAttr.setConnectable( True )
	uAttr.setReadable( True )
	uAttr.setWritable( False )
	
	#------------------------------

	hrGeneralMuscle.internalMuscleHeights = tAttr.create( "internalMuscleHeights", "iRh", OpenMaya.MFnData.kDoubleArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )
	
	hrGeneralMuscle.internalMuscleWidths = tAttr.create( "internalMuscleWidths", "iRw", OpenMaya.MFnData.kDoubleArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalMuscleLength = uAttr.create( "internalMuscleLength", "iRl", OpenMaya.MFnUnitAttribute.kDistance, 0.0 )
	uAttr.setStorable( True )
	uAttr.setHidden( True )
	uAttr.setConnectable( False )
	uAttr.setReadable( False )
	uAttr.setWritable( True )

	hrGeneralMuscle.internalInitialVolumes = tAttr.create( "internalInitialVolumes", "iIv", OpenMaya.MFnData.kDoubleArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalMusclePositions	= tAttr.create( "internalMusclePositions", "iMp", OpenMaya.MFnData.kPointArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalMuscleXsections	= tAttr.create( "internalMuscleXsections", "iXs", OpenMaya.MFnData.kNurbsCurve  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalMuscleCurve	= tAttr.create( "internalMuscleCurve", "icv", OpenMaya.MFnData.kNurbsCurve  )
	tAttr.setStorable( False )
	

	hrGeneralMuscle.internalVPoints = tAttr.create( "internalVPoints", "iVp", OpenMaya.MFnData.kVectorArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalWhichUp = tAttr.create( "internalWhichUp", "iwu", OpenMaya.MFnData.kIntArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )

	hrGeneralMuscle.internalMuscleLocks = tAttr.create( "internalMuscleLocks", "iml", OpenMaya.MFnData.kIntArray  )
	tAttr.setStorable( False )
	tAttr.setHidden( True )
	tAttr.setConnectable( False )
	tAttr.setReadable( False )
	tAttr.setWritable( False )
	
	#------------------------------

	hrGeneralMuscle.muscleSurface = tAttr.create( "muscleSurface", "ms", OpenMaya.MFnData.kNurbsSurface  )
	tAttr.setWritable(False)
	tAttr.setStorable(False)
	
	
	
	#==================================================
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.calculateVolume )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('calculateVolume', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.connectionPt )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('connectionPt', kPluginNodeTypeName ) )

	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.originVectorPt )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('originVectorPt', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.originVectorLock )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('originVectorLock', kPluginNodeTypeName ) )

	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.insertionVectorPt )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('insertionVectorPt', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.insertionVectorLock )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('insertionVectorLock', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restHeightO )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restHeightO', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restHeightOv )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restHeightOv', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restWidthOv )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restWidthOv', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restHeightIv )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restHeightIv', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restWidthIv )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restWidthIv', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.restHeightI )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('restHeightI', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.muscleLength )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('muscleLength', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleHeights )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleHeights', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleWidths )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleWidths', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleLength )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleLength', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalInitialVolumes )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalInitialVolumes', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalWhichUp )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalWhichUp', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleLocks )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleLocks', kPluginNodeTypeName ) )

	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMusclePositions )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMusclePositions', kPluginNodeTypeName ) )
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleXsections )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleXsections', kPluginNodeTypeName ) )

	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalVPoints )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalVPoints', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.internalMuscleCurve )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('internalMuscleCurve', kPluginNodeTypeName ) )
	
	try:
		hrGeneralMuscle.addAttribute( hrGeneralMuscle.muscleSurface )
	except:
		sys.stderr.write( "Failed to create %s of %s node\n" % ('muscleSurface', kPluginNodeTypeName ) )
	
	
	#==================================================
	
	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.calculateVolume, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorPt, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorPt, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightO, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightOv, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restWidthOv, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightIv, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restWidthIv, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightI, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorLock, hrGeneralMuscle.muscleSurface )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorLock, hrGeneralMuscle.muscleSurface )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'muscleSurface' )
	
	#-----------------------------------------

	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightO, hrGeneralMuscle.internalMuscleHeights )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightOv, hrGeneralMuscle.internalMuscleHeights )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightIv, hrGeneralMuscle.internalMuscleHeights )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restHeightI, hrGeneralMuscle.internalMuscleHeights )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.calculateVolume, hrGeneralMuscle.internalMuscleHeights )
		
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restWidthOv, hrGeneralMuscle.internalMuscleWidths )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.restWidthIv, hrGeneralMuscle.internalMuscleWidths )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.calculateVolume, hrGeneralMuscle.internalMuscleWidths )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalMuscleWidths )
	
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalMuscleWidths and Heights' )
		
	#----------------------------------------------

	
	#-----------------------------------------

	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.calculateVolume, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorPt, hrGeneralMuscle.internalMuscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorPt, hrGeneralMuscle.internalMuscleLength )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalMuscleLength' )
	
	#----------------------------------------------

	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorPt, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorPt, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorLock, hrGeneralMuscle.internalMusclePositions )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorLock, hrGeneralMuscle.internalMusclePositions )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalMusclePositions' )
	
	#----------------------------------------------
	
	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.internalWhichUp )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalWhichUp' )

	#----------------------------------------------

	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorPt, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorLock, hrGeneralMuscle.internalMuscleCurve )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorLock, hrGeneralMuscle.internalMuscleCurve )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalMuscleCurve' )

	#----------------------------------------------

	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.internalVPoints )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.internalVPoints )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.internalVPoints )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.internalVPoints )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.internalVPoints )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.internalVPoints )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalVPoints' )

	#----------------------------------------------
	
	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorLock, hrGeneralMuscle.internalMuscleLocks )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorLock, hrGeneralMuscle.internalMuscleLocks )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'internalMuscleLocks' )

	#----------------------------------------------
	
	try:
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionPt, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionSurface, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionU, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionV, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionUp, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.connectionFlip, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.originVectorPt, hrGeneralMuscle.muscleLength )
		hrGeneralMuscle.attributeAffects( hrGeneralMuscle.insertionVectorPt, hrGeneralMuscle.muscleLength )
	except:
		sys.stderr.write( "Failed to set attr affects to %s\n" % 'muscleLength' )

	

	
	
	
#==================================================
# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Paul G. Thuriot", "0.9.1", "Any") 
	
	try:
		mplugin.registerNode( kPluginNodeTypeName, hrGeneralMuscleID, nodeCreator, nodeInitializer )
	except:
		sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

	
# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( hrGeneralMuscleID )
	except:
		sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )