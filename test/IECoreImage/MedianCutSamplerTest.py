##########################################################################
#
#  Copyright (c) 2008-2009, Image Engine Design Inc. All rights reserved.
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
import os
import imath
import IECore
import IECoreImage

class MedianCutSamplerTest( unittest.TestCase ) :

	def test( self ) :

		image = IECore.Reader.create( os.path.join( "test", "IECoreImage", "data", "exr", "carPark.exr" ) ).read()
		for n in ["R", "G", "B"] :
			p = image[n]
			p.data = IECore.DataCastOp()( object=image[n], targetType=IECore.FloatVectorData.staticTypeId() )
			image[n] = p

		luminanceImage = IECoreImage.LuminanceOp()( input=image )

		s = IECoreImage.MedianCutSampler()( image=luminanceImage, subdivisionDepth=4, projection=IECoreImage.MedianCutSampler.Projection.LatLong )
		centroids = s["centroids"]
		areas = s["areas"]

		self.assertEqual( len( s ), 2 )
		self.assertEqual( len( centroids ), len( areas ) )
		self.assertEqual( len( centroids ), 16 )
		self.assertTrue( centroids.isInstanceOf( IECore.V2fVectorData.staticTypeId() ) )
		self.assertTrue( areas.isInstanceOf( IECore.Box2iVectorData.staticTypeId() ) )

		dataWindow = luminanceImage.dataWindow
		areaSum = 0
		for i in range( 0, len( centroids ) ) :
			c = centroids[i]
			c = imath.V2i( int(c.x), int(c.y) )
			self.assertTrue( dataWindow.intersects( c ) )
			self.assertTrue( areas[i].intersects( c ) )
			s = areas[i].size() + imath.V2i( 1 )
			areaSum += s.x * s.y

		self.assertEqual( areaSum, luminanceImage.channelSize() )

if __name__ == "__main__":
	unittest.main()

