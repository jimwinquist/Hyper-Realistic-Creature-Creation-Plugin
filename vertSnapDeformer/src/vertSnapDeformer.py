##############################################################################
'''
vertSnapDeformer.py
originally from Writing Creature Deformers
Erick Miller
copywrite 2009

converted to python -- Paul Thuriot

Python plugin for:
HYPER REAL 2 book - 2009


NOTE: There is a significant speed hit when using a python plugin versus a compiled C plugin.  The benefit is that this python plugin should work on any OS (Win/ Mac/ Linux) and Maya version (8.5+).

NOTE: Tested on Win (32/ 64) and Linux for Maya 8.5, 2008, +
'''
##############################################################################

import math, sys

import maya.cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


kPluginNodeTypeName = "vertSnapDeformer"

# CHANGE THIS ID AS NEEDED
vertSnapDeformerID = OpenMaya.MTypeId( 0x7269b )


#==================================================
# Node definition
class vertSnapDeformer( OpenMayaMPx.MPxDeformerNode ):
	#----------------------------------------
	# class variables
	driver_mesh = OpenMaya.MObject()		# driver object (the one the verts will snap to)
	initialized_data = OpenMaya.MObject()	# allows the vert mapping to be reset
	vert_map = OpenMaya.MObject()  # this is the array of associated vert indexes (interal node use)	
	
	
	#==================================================
	# constructor
	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)
	
	
	
	
	
	
	
	#==================================================
	# deform
	def deform( self, data, iter, localToWorldMatrix, mIndex ):
		initialized_mapping = data.inputValue( self.initialized_data ).asShort();
		
		#//////////////////////////////////////
		#/ Attribute based initializing for resetting the deform state:
		#/ (using an attr on the node)
		#/
		if( initialized_mapping == 1 ):
			self.initVertMapping(data, iter, localToWorldMatrix, mIndex)
			initialized_mapping = data.inputValue( self.initialized_data ).asShort()
	
		if( initialized_mapping == 2 ):  # //deformer data initialized successfully. begin deform.
	
			#get data from data block:
			envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
			envelopeHandle = data.inputValue( envelope )
			env = envelopeHandle.asFloat()
			
			vertMapArrayData  = data.inputArrayValue( self.vert_map )
			
			# attach to the poly function set :
			meshAttrHandle = data.inputValue( self.driver_mesh )
			meshMobj = OpenMaya.MObject()
			
			meshMobj = meshAttrHandle.asMesh()
			vertIter = OpenMaya.MItMeshVertex( meshMobj )
			
			
			# this is the deform loop:
			while( iter.isDone() == False ):
				weight = self.weightValue( data, mIndex, iter.index() ) #//painted weight
				ww = weight * env; #//weight * envelope value
					
				if ( ww != 0 ): #// filter out weights that are  zero
					vertMapArrayData.jumpToElement( iter.index() )
					index_mapped = vertMapArrayData.inputValue().asInt() #//get mapped index
					if( index_mapped >= 0 ): #// filter out un-mapped points
						util = OpenMaya.MScriptUtil()   
						prevInt = util.asIntPtr()   
					
						vertIter.setIndex( index_mapped, prevInt )
						
						mappedPt = OpenMaya.MPoint()
						mappedPt = vertIter.position( OpenMaya.MSpace.kWorld )	#// get in world space
					
						iterPt = OpenMaya.MPoint()
						iterPt = iter.position() * localToWorldMatrix 	#// get in world space by transforming
						
						pt = OpenMaya.MPoint()
						pt = iterPt + ((mappedPt - iterPt) * ww )		#// scale delta for painted weights
						pt = pt * localToWorldMatrix.inverse() 				#// transform new pt back into obj space
						iter.setPosition( pt )									#// set the point on the deforming mesh.
				
				iter.next()


	def initVertMapping( self, data, iter, localToWorldMatrix, mIndex):
		#make poly mesh function set object:
		meshAttrHandle = data.inputValue( self.driver_mesh  )
		meshMobj = meshAttrHandle.asMesh()
		vertIter = OpenMaya.MItMeshVertex( meshMobj )
		vertIter.reset()
		count = iter.count()
		
		vertMapOutArrayData = data.outputArrayValue( self.vert_map )
		
		vertMapOutArrayBuilder = OpenMaya.MArrayDataBuilder( self.vert_map, count )
		allPts = OpenMaya.MPointArray()
		allPts.clear()
		
		i = 0
		#first initialize all mappings to -1, and also store a buffer pt array to search through:
		while( iter.isDone() == False ):
			initIndexDataHnd = vertMapOutArrayBuilder.addElement( i )
			negIndex = -1
			
			initIndexDataHnd.setInt( negIndex )
			initIndexDataHnd.setClean()
			
			
			allPts.append( iter.position() * localToWorldMatrix )
			i = i+1
			iter.next()
			
		vertMapOutArrayData.set( vertMapOutArrayBuilder )
		
		while( vertIter.isDone() == False ):
			driver_pt = OpenMaya.MPoint()
			driver_pt = vertIter.position( OpenMaya.MSpace.kWorld )
			closest_pt_index = self.getClosestPt( driver_pt, allPts )
			#save the closest point mapping to snap verts to each other here:
			
			snapDataHnd = vertMapOutArrayBuilder.addElement( closest_pt_index )
			snapDataHnd.setInt( vertIter.index() )
			
			snapDataHnd.setClean()
			vertIter.next()
		
		vertMapOutArrayData.set( vertMapOutArrayBuilder )
	
		tObj  =  self.thisMObject()
		
		setInitMode = OpenMaya.MPlug( tObj, self.initialized_data  )
		setInitMode.setShort( 2 ) 
	
		iter.reset() #important, reset the geom iterator so it starts from zero again
	
	
	#this is really a brute force linear closest pt function,
	#definately nothing fancy here (returns the pt index, not the point):
	def getClosestPt( self, pt, points ):
		ptIndex=0
		currentDistance = 9e99
		furthestDistanceSoFar = 9e99
		for i in range( 0, points.length() ):
			currentDistance = pt.distanceTo( points[i] )
			if(currentDistance < furthestDistanceSoFar ):
				ptIndex = i 
				furthestDistanceSoFar = currentDistance
			
		return ( ptIndex )
	
	
	
	
	
	
	
	
	
#==================================================	
# creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( vertSnapDeformer() )

#==================================================
# initializer
def nodeInitializer():
	numericAttr = OpenMaya.MFnNumericAttribute()
	polyMeshAttr = OpenMaya.MFnTypedAttribute()
	enumAttr = OpenMaya.MFnEnumAttribute()
	
	
	vertSnapDeformer.driver_mesh = polyMeshAttr.create( "vertSnapInput", "vsnpin", OpenMaya.MFnData.kMesh )
	polyMeshAttr.setStorable(False)
	polyMeshAttr.setConnectable(True)
	vertSnapDeformer.addAttribute( vertSnapDeformer.driver_mesh )
	vertSnapDeformer.attributeAffects( vertSnapDeformer.driver_mesh, OpenMayaMPx.cvar.MPxDeformerNode_outputGeom )

	vertSnapDeformer.initialized_data = enumAttr.create( "initialize", "inl" )
	enumAttr.addField(	"Off", 0)
	enumAttr.addField(	"Re-Set Bind", 1)	
	enumAttr.addField(	"Bound", 2)
	enumAttr.setKeyable(True)
	enumAttr.setStorable(True)
	enumAttr.setReadable(True)
	enumAttr.setWritable(True)
	enumAttr.setDefault(0)
	vertSnapDeformer.addAttribute( vertSnapDeformer.initialized_data )
	vertSnapDeformer.attributeAffects( vertSnapDeformer.initialized_data, OpenMayaMPx.cvar.MPxDeformerNode_outputGeom )	

	vertSnapDeformer.vert_map = numericAttr.create( "vtxIndexMap", "vtximp", OpenMaya.MFnNumericData.kLong )
	numericAttr.setKeyable(False)
	numericAttr.setArray(True)
	numericAttr.setStorable(True)
	numericAttr.setReadable(True)
	numericAttr.setWritable(True)
	vertSnapDeformer.addAttribute( vertSnapDeformer.vert_map )
	vertSnapDeformer.attributeAffects( vertSnapDeformer.vert_map, OpenMayaMPx.cvar.MPxDeformerNode_outputGeom  )

	# make weights paintable
	maya.cmds.makePaintable( kPluginNodeTypeName, 'weights', attrType='multiFloat' )
	
	
#==================================================
# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Erick Miller - Paul Thuriot", "1.0.1") 
	try:
		mplugin.registerNode( kPluginNodeTypeName, vertSnapDeformerID, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode )
	except:
		sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( vertSnapDeformerID )
	except:
		sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )

		