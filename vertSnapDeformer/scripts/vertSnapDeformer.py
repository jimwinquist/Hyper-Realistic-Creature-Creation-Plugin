"""

Title: vertSnapDeformer.py

Required: vertSnapDeformer.mll (or vertSnapDeformer.so)

Author: Erick Miller (convert to python  --  Webber Huang)

Date: April 2005 

Version: 1.0

Description:

    Select the driver poly mesh (the one that will get snapped to) and 
    then shift select the driven object (the one you want to deform)
    and run the command:

    vertSnapDeformer();


Return:     creates & returns a deformer node of "vertSnapDeformer" type.

"""
import maya.cmds as cmd

__PLUIN_BASENAME__ = 'vertSnapDeformer'

#----------------------------------------------------------------------
def create():
    """"""
    isLoad = loadPlugin()
    
    sel = cmd.ls(sl=1, ap=1)
    
    if isLoad:
        if len(sel) != 2 or\
        (len(cmd.listRelatives(sel[0], type='mesh')) == 0 and cmd.nodeType(sel[0]) != 'mesh') or\
        (len(cmd.listRelatives(sel[1], type='mesh')) == 0 and cmd.nodeType(sel[1]) != 'mesh') :
            cmd.error(" Select the polygon driver geometry first, and the polygon mesh to be deformed last.")
        else:
            defr = cmd.deformer(sel[1], type='vertSnapDeformer')[0]
            cmd.connectAttr('%s.worldMesh[0]' % sel[0], '%s.vertSnapInput' % defr)
            cmd.setAttr('%s.initialize' % defr, 1)
    else:
        cmd.error("Copy the vertSnapDeformer plugin into the MAYA_PLUGIN_PATH.")
    
    return defr

#----------------------------------------------------------------------
def loadPlugin():
    """"""
    mayaVersion = cmd.about(v=1).split(' ')
    
    if cmd.about(os=1) == 'win64':
        if int(mayaVersion[0]) < 2014:
            pluginName = '%s_%s-%s.mll' % (__PLUIN_BASENAME__, mayaVersion[0], mayaVersion[1])
        else:
            pluginName = '%s_%s-x64.mll' % (__PLUIN_BASENAME__, mayaVersion[0])
    elif cmd.about(os=1) == 'mac':
        pluginName = '%s_%s.bundle' % (__PLUIN_BASENAME__, mayaVersion[0])
    elif cmd.about(os=1) == 'linux64':
        pluginName = '%s_%s.so' % (__PLUIN_BASENAME__, mayaVersion[0])
    else:
        cmd.error('vertSnapDeformer is available for 64bit version of Autodesk Maya 2011 '
                  'or above under Windows 64bit, Mac OS X and Linux 64bit!')
    
    if not cmd.pluginInfo(pluginName, q=True, l=True ):
        cmd.loadPlugin(pluginName)
    
    return cmd.pluginInfo(pluginName, q=True, l=True )