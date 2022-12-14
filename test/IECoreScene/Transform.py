##########################################################################
#
#  Copyright (c) 2007, Image Engine Design Inc. All rights reserved.
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
import unittest
import imath
import IECore
import IECoreScene

class TestTransform( unittest.TestCase ) :

	def test( self ) :

		m = IECoreScene.MatrixTransform( imath.M44f() )
		self.assertEqual( m.transform(), imath.M44f() )
		self.assertEqual( m.transform( 1 ), imath.M44f() )
		self.assertEqual( m.matrix, imath.M44f() )

		m = IECoreScene.MatrixTransform( imath.M44f().translate( imath.V3f( 1, 2, 3 ) ) )
		self.assertEqual( m.transform(), imath.M44f().translate( imath.V3f( 1, 2, 3 ) ) )
		self.assertEqual( m.transform( 1 ), imath.M44f().translate( imath.V3f( 1, 2, 3 ) ) )
		self.assertEqual( m.matrix, imath.M44f().translate( imath.V3f( 1, 2, 3 ) ) )

		mm = m.copy()

		self.assertEqual( m, mm )

		IECore.Writer.create( mm, os.path.join( "test", "transform.cob" ) ).write()
		mmm = IECore.Reader.create( os.path.join( "test", "transform.cob" ) ).read()

		self.assertEqual( mm, mmm )

	def testMotionTransform( self ) :

		m = IECoreScene.MatrixMotionTransform()
		self.assertEqual( m.transform(), imath.M44f() )
		self.assertEqual( m.transform( 2 ), imath.M44f() )
		self.assertEqual( m.keys(), [] )
		self.assertEqual( m.values(), [] )
		self.assertEqual( len( m ), 0 )

		t1 = imath.M44f().translate( imath.V3f( 0, 1, 0 ) )
		t2 = imath.M44f().translate( imath.V3f( 0, 5, 0 ) )
		tMid = imath.M44f().translate( imath.V3f( 0, 3, 0 ) )

		m[0] = t1
		self.assertEqual( len( m ), 1 )
		self.assertEqual( m.keys(), [ 0 ] )
		self.assertEqual( m.values(), [ t1 ] )
		self.assertEqual( m.transform(), t1 )
		self.assertEqual( m.transform( -1 ), t1 )
		self.assertEqual( m.transform( 0 ), t1 )
		self.assertEqual( m.transform( 1 ), t1 )

		m[1] = t2
		self.assertEqual( len( m ), 2 )
		self.assertEqual( m.keys(), [ 0, 1 ] )
		self.assertEqual( m.values(), [ t1, t2 ] )
		self.assertEqual( m.transform(), t1 )
		self.assertEqual( m.transform( -1 ), t1 )
		self.assertEqual( m.transform( 1 ), t2 )
		self.assertEqual( m.transform( 2 ), t2 )
		self.assertEqual( m.transform( 0.5 ), tMid )

		mm = m.copy()

		self.assertEqual( m, mm )

		IECore.Writer.create( mm, os.path.join( "test", "motionTransform.cob" ) ).write()
		mmm = IECore.Reader.create( os.path.join( "test", "motionTransform.cob" ) ).read()

		self.assertEqual( mm, mmm )

	def testHash( self ) :

		t = IECoreScene.MatrixTransform( imath.M44f() )
		self.assertEqual( t.hash(), IECoreScene.MatrixTransform( imath.M44f() ).hash() )

		t2 = IECoreScene.MatrixTransform( imath.M44f().translate( imath.V3f( 1 ) ) )
		self.assertNotEqual( t.hash(), t2.hash() )

	def tearDown( self ) :

		if os.path.isfile(os.path.join( "test", "motionTransform.cob" )):
			os.remove(os.path.join( "test", "motionTransform.cob" ))

		if os.path.isfile(os.path.join( "test", "transform.cob" )):
			os.remove(os.path.join( "test", "transform.cob" ))

if __name__ == "__main__":
	unittest.main()

