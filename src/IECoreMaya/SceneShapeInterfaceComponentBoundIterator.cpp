//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2007-2013, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "IECoreMaya/SceneShapeInterfaceComponentBoundIterator.h"

#include "maya/MFnSingleIndexedComponent.h"

using namespace IECoreMaya;

SceneShapeInterfaceComponentBoundIterator::SceneShapeInterfaceComponentBoundIterator( void *userGeometry, MObjectArray &components )
	: 	MPxGeometryIterator( userGeometry, components ),
		m_sceneShapeInterface( (SceneShapeInterface*) userGeometry ),
		m_idx( 0 ),
		m_components( components )
{
	computeNumComponents();
}

SceneShapeInterfaceComponentBoundIterator::SceneShapeInterfaceComponentBoundIterator( void *userGeometry, MObject &components )
	: 	MPxGeometryIterator( userGeometry, components ),
		m_sceneShapeInterface( (SceneShapeInterface*) userGeometry ),
		m_idx( 0 )
{
	m_components.append( components );
	computeNumComponents();
}

void SceneShapeInterfaceComponentBoundIterator::computeNumComponents()
{
	MStatus s;
	m_numComponents = 0;
	for( unsigned j=0; j < m_components.length(); ++j )
	{
		MFnSingleIndexedComponent fnCmp( m_components[j], &s );
		if( s )
		{
			m_numComponents += fnCmp.elementCount();
		}
	}
}

void SceneShapeInterfaceComponentBoundIterator::reset()
{
	m_idx = 0;
}

MPoint SceneShapeInterfaceComponentBoundIterator::point() const
{
	MPoint ret;

	Imath::Box3d bbox = m_sceneShapeInterface->componentBound( index() );

	switch( m_idx % 8 )
	{
		case 0: ret = MPoint( bbox.min[0], bbox.min[1], bbox.min[2] ); break;
		case 1: ret = MPoint( bbox.max[0], bbox.min[1], bbox.min[2] ); break;
		case 2: ret = MPoint( bbox.min[0], bbox.max[1], bbox.min[2] ); break;
		case 3: ret = MPoint( bbox.max[0], bbox.max[1], bbox.min[2] ); break;
		case 4: ret = MPoint( bbox.min[0], bbox.min[1], bbox.max[2] ); break;
		case 5: ret = MPoint( bbox.max[0], bbox.min[1], bbox.max[2] ); break;
		case 6: ret = MPoint( bbox.min[0], bbox.max[1], bbox.max[2] ); break;
		case 7: ret = MPoint( bbox.max[0], bbox.max[1], bbox.max[2] ); break;
		default: break;
	}

	return ret;
}

void SceneShapeInterfaceComponentBoundIterator::setPoint( const MPoint & ) const
{
}

int SceneShapeInterfaceComponentBoundIterator::iteratorCount() const
{
	// one for each bounding box corner
	return m_numComponents * 8;
}

bool SceneShapeInterfaceComponentBoundIterator::hasPoints() const
{
	return true;
}


bool SceneShapeInterfaceComponentBoundIterator::isDone() const
{
	return m_idx >= m_numComponents * 8;
}

#if MAYA_API_VERSION < 202200
void SceneShapeInterfaceComponentBoundIterator::next()
{
	++m_idx;
}
#else
MStatus SceneShapeInterfaceComponentBoundIterator::next()
{
	if( isDone() )
	{
		return MS::kFailure;
	}

	++m_idx;

	return MS::kSuccess;
}
#endif

void SceneShapeInterfaceComponentBoundIterator::component( MObject &component )
{
	component = MObject::kNullObj;
}

int SceneShapeInterfaceComponentBoundIterator::setPointGetNext(MPoint &p)
{
	return m_idx + 1;
}

int SceneShapeInterfaceComponentBoundIterator::index() const
{
	MStatus s;
	unsigned componentNum = 0;
	unsigned targetComponentNum = m_idx / 8;
	for( unsigned j=0; j < m_components.length(); ++j )
	{
		MFnSingleIndexedComponent fnCmp( m_components[j], &s );
		if( s )
		{
			if( componentNum + fnCmp.elementCount() > targetComponentNum )
			{
				return fnCmp.element( targetComponentNum - componentNum );
			}
			componentNum += fnCmp.elementCount();
		}
	}
	return 0;
}

bool SceneShapeInterfaceComponentBoundIterator::hasNormals() const
{
	return false;
}

int SceneShapeInterfaceComponentBoundIterator::indexUnsimplified() const
{
	return m_idx;
}
