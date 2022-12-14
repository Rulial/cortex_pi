##########################################################################
#
#  Copyright (c) 2009-2013, Image Engine Design Inc. All rights reserved.
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

import unittest
import os.path
import shutil
import imath

import IECore
import IECoreScene
import IECoreImage

import IECoreGL
IECoreGL.init( False )

class DiskPrimitiveTest( unittest.TestCase ) :

	outputFileName = os.path.join( os.path.dirname( __file__ ), "output", "testDisk.tif" )

	def test( self ) :

		r = IECoreGL.Renderer()
		r.setOption( "gl:mode", IECore.StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", IECore.StringData( os.path.join( os.path.dirname( __file__ ), "shaders" ) ) )

		r.camera( "main", {
				"projection" : IECore.StringData( "orthographic" ),
				"resolution" : IECore.V2iData( imath.V2i( 256 ) ),
				"clippingPlanes" : IECore.V2fData( imath.V2f( 1, 1000 ) ),
				"screenWindow" : IECore.Box2fData( imath.Box2f( imath.V2f( -1 ), imath.V2f( 1 ) ) )
			}
		)
		r.display( self.outputFileName, "tif", "rgba", {} )

		with IECoreScene.WorldBlock( r ) :

			r.concatTransform( imath.M44f().translate( imath.V3f( 0, 0, -5 ) ) )

			r.shader( "surface", "color", { "colorValue" : IECore.Color3fData( imath.Color3f( 0, 0, 1 ) ) } )
			r.disk( 1, 0, 360, {} )

		i = IECore.Reader.create( self.outputFileName ).read()
		reader = IECore.Reader.create( os.path.join( os.path.dirname( __file__ ), "images", "disk.tif" ) )
		reader["rawChannels"].setTypedValue( True )
		i2 = reader.read()

		# blue where there must be an object
		# red where we don't mind
		# black where there must be nothing

		a = i["A"]

		r2 = i2["R"]
		b2 = i2["B"]
		for i in range( r2.size() ) :

			if b2[i] > 0.5 :
				self.assertEqual( a[i], 1 )
			elif r2[i] < 0.5 :
				self.assertEqual( a[i], 0 )

	def testWindingOrder( self ) :

		# camera facing single sided - should be visible

		r = IECoreGL.Renderer()
		r.setOption( "gl:mode", IECore.StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", IECore.StringData( os.path.join( os.path.dirname( __file__ ), "shaders" ) ) )

		r.camera( "main", {
				"projection" : IECore.StringData( "orthographic" ),
				"resolution" : IECore.V2iData( imath.V2i( 256 ) ),
				"clippingPlanes" : IECore.V2fData( imath.V2f( 1, 1000 ) ),
				"screenWindow" : IECore.Box2fData( imath.Box2f( imath.V2f( -1 ), imath.V2f( 1 ) ) )
			}
		)
		r.display( self.outputFileName, "tif", "rgba", {} )

		with IECoreScene.WorldBlock( r ) :

			r.concatTransform( imath.M44f().translate( imath.V3f( 0, 0, -5 ) ) )
			r.setAttribute( "doubleSided", IECore.BoolData( False ) )

			r.shader( "surface", "color", { "colorValue" : IECore.Color3fData( imath.Color3f( 0, 0, 1 ) ) } )
			r.disk( 1, 0, 360, {} )

		image = IECore.Reader.create( self.outputFileName ).read()
		dimensions = image.dataWindow.size() + imath.V2i( 1 )
		index = dimensions.x * dimensions.y//2 + dimensions.x//2
		self.assertEqual( image["A"][index], 1 )

		# back facing single sided - should be invisible

		r = IECoreGL.Renderer()
		r.setOption( "gl:mode", IECore.StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", IECore.StringData( os.path.join( os.path.dirname( __file__ ), "shaders" ) ) )

		r.camera( "main", {
				"projection" : IECore.StringData( "orthographic" ),
				"resolution" : IECore.V2iData( imath.V2i( 256 ) ),
				"clippingPlanes" : IECore.V2fData( imath.V2f( 1, 1000 ) ),
				"screenWindow" : IECore.Box2fData( imath.Box2f( imath.V2f( -1 ), imath.V2f( 1 ) ) )
			}
		)
		r.display( self.outputFileName, "tif", "rgba", {} )

		with IECoreScene.WorldBlock( r ) :

			r.concatTransform( imath.M44f().translate( imath.V3f( 0, 0, -5 ) ) )
			r.setAttribute( "doubleSided", IECore.BoolData( False ) )
			r.setAttribute( "rightHandedOrientation", IECore.BoolData( False ) )

			r.shader( "surface", "color", { "colorValue" : IECore.Color3fData( imath.Color3f( 0, 0, 1 ) ) } )
			r.disk( 1, 0, 360, {} )

		image = IECore.Reader.create( self.outputFileName ).read()
		dimensions = image.dataWindow.size() + imath.V2i( 1 )
		index = dimensions.x * dimensions.y//2 + dimensions.x//2
		self.assertEqual( image["A"][index], 0 )

	def setUp( self ) :

		if not os.path.isdir( os.path.join( "test", "IECoreGL", "output" ) ) :
			os.makedirs( os.path.join( "test", "IECoreGL", "output" ) )

	def tearDown( self ) :

		if os.path.isdir( os.path.join( "test", "IECoreGL", "output" ) ) :
			shutil.rmtree( os.path.join( "test", "IECoreGL", "output" ) )

if __name__ == "__main__":
    unittest.main()
