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

import unittest
import os
import IECore
import IECoreScene

class TestRemovePrimVar( unittest.TestCase ) :

	def test( self ) :

		r = IECore.Reader.create( os.path.join( "test", "IECore", "data", "pdcFiles", "particleShape1.250.pdc" ) )
		p = r.read()
		numPrimVars = len( p )

		toRemove = [ "particleId", "mass", "lastWorldVelocity", "worldVelocityInObjectSpace" ]
		for n in toRemove :
			self.assertTrue( n in p )

		o = IECoreScene.RemovePrimitiveVariables()
		o["input"].setValue( p )
		o["names"].setValue( IECore.StringVectorData( toRemove ) )

		pp = o()
		self.assertEqual( len( pp ), numPrimVars - len( toRemove ) )
		for n in toRemove :
			self.assertTrue( not n in pp )

		for n in toRemove :
			self.assertTrue( not n in pp )

		self.assertTrue( not pp.isSame( p ) )

		o["copyInput"].setValue( IECore.BoolData( False ) )
		ppp = o()
		self.assertTrue( ppp.isSame( p ) )

if __name__ == "__main__":
	unittest.main()

