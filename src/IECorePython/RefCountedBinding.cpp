//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2007-2014, Image Engine Design Inc. All rights reserved.
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

// This include needs to be the very first to prevent problems with warnings
// regarding redefinition of _POSIX_C_SOURCE
#include "boost/python.hpp"

#include "IECorePython/RefCountedBinding.h"

#include "IECorePython/WrapperGarbageCollector.h"

#include "IECore/RefCounted.h"

using namespace boost::python;
using namespace IECore;

namespace IECorePython
{

static bool equal( const RefCounted *s, object other )
{
	extract<const RefCounted *> e( other );
	if( !e.check() )
	{
		return false;
	}
	return s == e();
}

static bool notEqual( const RefCounted *s, object other )
{
	return !equal( s, other );
}

static bool is( const RefCounted *s, const RefCounted *other )
{
	return s==other;
}

static uint64_t hash( const RefCounted *s )
{
	return reinterpret_cast<uint64_t>( s ) / sizeof( RefCounted );
}

void bindRefCounted()
{
	class_<RefCounted, boost::noncopyable, Detail::GILReleasePtr<RefCounted> >( "RefCounted", "A simple class to count references." )
		.def( "__eq__", equal )
		.def( "__ne__", notEqual )
		.def( "__hash__", hash )
		.def( "isSame", &is )
		.def( "refCount", &RefCounted::refCount )
		.def( "numWrappedInstances", &WrapperGarbageCollector::numWrappedInstances ).staticmethod( "numWrappedInstances" )
		.add_static_property( "garbageCollectionThreshold", &WrapperGarbageCollector::getCollectThreshold, &WrapperGarbageCollector::setCollectThreshold )
		.def( "collectGarbage", &WrapperGarbageCollector::collect ).staticmethod( "collectGarbage" )
	;

	Detail::IntrusivePtrToPython<RefCounted>();
	Detail::IntrusivePtrFromPython<RefCounted>();

	implicitly_convertible<RefCountedPtr, ConstRefCountedPtr>();
}

}

