##########################################################################
#
#  Copyright (p) 2009-2013, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import os.path
import math
import unittest
import imath
import IECore
import IECoreScene

class PatchMeshPrimitiveTest( unittest.TestCase ) :

	def testConstructors( self ) :

		self.assertRaises( Exception, IECoreScene.PatchMeshPrimitive )

		p = IECoreScene.PatchMeshPrimitive( 10, 7, IECore.CubicBasisf.bezier(), IECore.CubicBasisf.bezier(), False, False, IECore.V3fVectorData( [ imath.V3f() ] * 70 ) )

		self.assertEqual( p.uBasis(), IECore.CubicBasisf.bezier() )
		self.assertEqual( p.vBasis(), IECore.CubicBasisf.bezier() )
		self.assertEqual( p.uPeriodic(), False )
		self.assertEqual( p.vPeriodic(), False )
		self.assertEqual( p.keys(), [ "P" ] )
		self.assertEqual( p["P"].data.getInterpretation(), IECore.GeometricData.Interpretation.Point )
		self.assertEqual( p.uPoints(), 10 )
		self.assertEqual( p.vPoints(), 7 )
		self.assertEqual( p.uPatches(), 3 )
		self.assertEqual( p.vPatches(), 2 )
		self.assertTrue( p.arePrimitiveVariablesValid() )

	def testConstructorValidation( self ) :

		self.assertRaises( Exception, IECoreScene.PatchMeshPrimitive, 0, 0 )
		self.assertRaises( Exception, IECoreScene.PatchMeshPrimitive, 0, 1 )
		self.assertRaises( Exception, IECoreScene.PatchMeshPrimitive, 1, 0 )

	def testCopy( self ) :

		p = IECoreScene.PatchMeshPrimitive( 10, 7, IECore.CubicBasisf.bezier(), IECore.CubicBasisf.bezier(), False, False, IECore.V3fVectorData( [ imath.V3f() ] * 70 ) )

		pp = p.copy()
		self.assertEqual( p, pp )

	def testIO( self ) :

		p = IECoreScene.PatchMeshPrimitive( 10, 7, IECore.CubicBasisf.bezier(), IECore.CubicBasisf.bezier(), False, False )

		IECore.Writer.create( p, os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) ).write()

		pp = IECore.Reader.create( os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) ).read()

		self.assertEqual( pp, p )

	def testVariableSize( self ) :

		p = IECoreScene.PatchMeshPrimitive( 10, 7, IECore.CubicBasisf.bezier(), IECore.CubicBasisf.bezier(), False, False, IECore.V3fVectorData( [ imath.V3f() ] * 70 ) )

		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Constant ), 1 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Uniform ), 6 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Vertex ), 70 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Varying ), 12 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.FaceVarying ), 12 )

		p = IECoreScene.PatchMeshPrimitive( 9, 5, IECore.CubicBasisf.catmullRom(), IECore.CubicBasisf.catmullRom(), True, False, IECore.V3fVectorData( [ imath.V3f() ] * 45 ) )

		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Constant ), 1 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Uniform ), 18 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Vertex ), 45 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.Varying ), 27 )
		self.assertEqual( p.variableSize( IECoreScene.PrimitiveVariable.Interpolation.FaceVarying ), 27 )

	def setUp( self ) :

		if os.path.isfile( os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) ) :
			os.remove( os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) )

	def tearDown( self ) :

		if os.path.isfile( os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) ) :
			os.remove( os.path.join( "test", "IECore", "data", "PatchMeshPrimitive.cob" ) )

if __name__ == "__main__":
    unittest.main()

