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
import os.path

import IECore
import IECoreScene

class TestTypedPrimitiveOp( unittest.TestCase ) :

	class MeshCopyOp( IECoreScene.MeshPrimitiveOp ) :

		def __init__( self ):

			IECoreScene.MeshPrimitiveOp.__init__( self, "MeshCopyOp : A simple op to copy meshes" )

		def modifyTypedPrimitive( self, mesh, operands ) :

			# ModifyOp should automatically copy the input for us, so we can just
			# return it.

			return mesh

	def testMeshPrimitiveOp( self ) :
		""" Test TypedPrimitiveOp for use with MeshPrimitive """
		op = TestTypedPrimitiveOp.MeshCopyOp()

		inputMesh = IECoreScene.MeshPrimitive()

		outputMesh = op( input = inputMesh )

		self.assertTrue( outputMesh.isInstanceOf( IECoreScene.TypeId.MeshPrimitive ) )
		self.assertFalse( inputMesh is outputMesh )
		self.assertEqual( inputMesh, outputMesh )

if __name__ == "__main__":
        unittest.main()
