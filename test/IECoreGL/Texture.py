##########################################################################
#
#  Copyright (c) 2007-2010, Image Engine Design Inc. All rights reserved.
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

from __future__ import with_statement

import unittest
import os.path
import shutil
import imath

import IECore
import IECoreScene
import IECoreImage
import IECoreGL

IECoreGL.init( False )

class TestTexture( unittest.TestCase ) :

	def testConstructor( self ) :

		i = IECore.Reader.create( os.path.join( os.path.dirname( __file__ ), "images", "colorBarsWithAlphaF512x512.exr" ) ).read()

		t = IECoreGL.ColorTexture( i )
		self.assertTrue( isinstance( t, IECoreGL.ColorTexture ) )

		ii = t.imagePrimitive()
		self.assertTrue( isinstance( ii, IECoreImage.ImagePrimitive ) )
		self.assertEqual( sorted( ii.keys() ), [ "A", "B", "G", "R" ] )
		self.assertTrue( ii.channelsValid() )

	def performShaderParameterTest( self, shaderParameter ) :

		outputFileName = os.path.join( os.path.dirname( __file__ ), "output", "testTexture.tif" )

		r = IECoreGL.Renderer()
		r.setOption( "gl:mode", IECore.StringData( "immediate" ) )

		r.camera( "main", {
				"projection" : IECore.StringData( "perspective" ),
				"projection:fov" : IECore.FloatData( 45 ),
				"resolution" : IECore.V2iData( imath.V2i( 256 ) ),
				"clippingPlanes" : IECore.V2fData( imath.V2f( 1, 1000 ) ),
				"screenWindow" : IECore.Box2fData( imath.Box2f( imath.V2f( -0.5 ), imath.V2f( 0.5 ) ) )
			}
		)
		r.display( outputFileName, "tif", "rgba", {} )

		vs = """
		void main()
		{
			gl_Position = ftransform();
			gl_TexCoord[0] = gl_MultiTexCoord0;
		}
		"""

		fs = """
		uniform sampler2D testSampler;
		void main()
		{
			gl_FragColor = vec4( texture2D( testSampler, gl_TexCoord[0].xy ).rgb, 1.0 );
		}
		"""

		with IECoreScene.WorldBlock( r ) :

			r.concatTransform( imath.M44f().translate( imath.V3f( 0, 0, -5 ) ) )

			r.shader( "surface", "color",
				{
					"gl:vertexSource" : vs,
					"gl:fragmentSource" : fs,
					"testSampler" : shaderParameter,
				}
			)

			r.sphere( 1, -1, 1, 360, {} )

	def testEmptyStringShaderParameter( self ) :

		self.performShaderParameterTest( IECore.StringData( "" ) )

	def testMissingStringShaderParameter( self ) :

		self.performShaderParameterTest( IECore.StringData( "thisFileDoesntExist" ) )

	def setUp( self ) :

		if not os.path.isdir( os.path.join( "test", "IECoreGL", "output" ) ) :
			os.makedirs( os.path.join( "test", "IECoreGL", "output" ) )

	def tearDown( self ) :

		if os.path.isdir( os.path.join( "test", "IECoreGL", "output" ) ) :
			shutil.rmtree( os.path.join( "test", "IECoreGL", "output" ) )

if __name__ == "__main__":
    unittest.main()
