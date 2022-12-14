//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2011-2013, Image Engine Design Inc. All rights reserved.
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

#include "IECorePython/LRUCacheBinding.h"

#include "IECorePython/ExceptionAlgo.h"
#include "IECorePython/ScopedGILRelease.h"

#include "IECore/LRUCache.h"

#include "boost/format.hpp"

#include "tbb/parallel_for.h"

#include <mutex>

using namespace boost::python;
using namespace IECore;
using namespace tbb;

namespace boost
{
namespace python
{

inline size_t hash_value( const boost::python::object &o )
{
	return PyObject_Hash( o.ptr() );
}

} // namespace boost
} // namespace python

namespace
{

struct LRUCacheGetter
{
	LRUCacheGetter( object g )
		:	getter( g )
	{
	}

	object operator() ( object key, LRUCache<object, object>::Cost &cost )
	{
		try
		{
			tuple t = extract<tuple>( getter( key ) );
			cost = extract<LRUCache<object, object>::Cost>( t[1] );
			return t[0];
		}

		catch( const boost::python::error_already_set & )
		{
			IECorePython::ExceptionAlgo::translatePythonException();
		}

	}

	object getter;
};

class PythonLRUCache : public LRUCache<object, object>
{

	public :

		PythonLRUCache( object getter, LRUCache<object, object>::Cost maxCost )
			:	LRUCache<object, object>( LRUCacheGetter( getter ), maxCost )
		{
		}

		PythonLRUCache( object getter, object removalCallback, LRUCache<object, object>::Cost maxCost )
			:	LRUCache<object, object>( LRUCacheGetter( getter ), removalCallback, maxCost )
		{
		}

		object get( const object &key )
		{
			// we must hold the GIL when entering LRUCache<object, object>::get()
			// or any other of our base class' methods, because they manipulate
			// boost::python::objects, which in turn use the python api. in addition,
			// LRUCacheGetter enters python, giving us another reason to need the
			// GIL. things are complicated slightly by the fact that the python code
			// executed by LRUCacheGetter may release the GIL, either explicitly or
			// because the interpreter does that from time to time anyway. this can
			// allow another thread to make a call to get(), potentially with the same
			// key as was passed to the current call. this would lead to deadlock -
			// the first call doing the caching waits for the GIL to continue,
			// and the second call holds the GIL and waits for the caching to be
			// complete.
			//
			// the code below avoids this, by ensuring only one thread can be in
			// LRUCache<object, object>::get(), at any given time, and by releasing
			// the GIL while it waits for m_getMutex. this allows the first thread
			// to finish caching (because it can reacquire the GIL), at which point
			// it will release m_getMutex, allowing the second thread to go about
			// its business.
			//
			// while this serialisation may seem inefficient, it's less of a big
			// deal because all python execution is serialised anyway.
			//
			// see test/IECore/LRUCache.py, in particular testYieldGILInGetter().

			std::unique_lock<Mutex> lock( m_getMutex, std::defer_lock );
			{
				IECorePython::ScopedGILRelease gilRelease;
				lock.lock();
			}
			return LRUCache<object, object>::get( key );
		}

	private :

		typedef std::mutex Mutex;
		Mutex m_getMutex;

};

typedef LRUCache<int, int> TestCache;

int get( int key, size_t &cost )
{
	cost = 1;
	return key;
}

struct GetFromTestCache
{
	public :

		GetFromTestCache( TestCache &cache, size_t numValues, size_t clearFrequency )
			:	m_cache( cache ), m_numValues( numValues ), m_clearFrequency( clearFrequency )
		{
		}

		void operator()( const blocked_range<size_t> &r ) const
		{
			for( size_t i=r.begin(); i!=r.end(); ++i )
			{
				const int k = i % m_numValues;
				const int v = m_cache.get( k );
				if( k != v )
				{
					throw Exception(
						boost::str(
							boost::format( "Incorrect LRUCache value found (expected %d but got %d)" ) % k %v
						)
					);
				}

				if( m_clearFrequency && (i % m_clearFrequency == 0) )
				{
					m_cache.clear();
				}
			}
		}

	private :

		TestCache &m_cache;
		size_t m_numValues;
		size_t m_clearFrequency;

};

void testLRUCacheThreading( int numIterations, int numValues, int maxCost, int clearFrequency = 0 )
{
	// do lots of parallel cache accesses. then clear the cache in the main
	// thread and check that it has emptied successfully, to ensure that the
	// cost counting has been accurate.

	TestCache cache( get, maxCost );
	tbb::task_group_context taskGroupContext( tbb::task_group_context::isolated );
	parallel_for( blocked_range<size_t>( 0, numIterations ), GetFromTestCache( cache, numValues, clearFrequency ), taskGroupContext);

	if( cache.currentCost() > cache.getMaxCost() )
	{
		throw Exception( "LRUCache exceeds maximum cost" );
	}

	cache.clear();
	if( cache.currentCost() != 0 )
	{
		throw Exception( "Cost not 0 after LRUCache::clear()" );
	}

	// as above, but using setMaxCost( 0 ) to clear the cache.

	TestCache cache2( get, maxCost );
	parallel_for( blocked_range<size_t>( 0, numIterations ), GetFromTestCache( cache2, numValues, clearFrequency ), taskGroupContext );

	if( cache2.currentCost() > cache2.getMaxCost() )
	{
		throw Exception( "LRUCache exceeds maximum cost" );
	}

	cache2.setMaxCost( 0 );
	if( cache2.currentCost() != 0 )
	{
		throw Exception( "Cost not 0 after LRUCache::setMaxCost( 0 )" );
	}
}

typedef LRUCache<int, int, LRUCachePolicy::Serial> SerialTestCache;
typedef LRUCache<int, int, LRUCachePolicy::Parallel> ParallelTestCache;

template<typename Cache>
Cache &recursiveCache();

template<typename Cache>
int getRecursive( int key, size_t &cost )
{
	cost = 1;
	switch( key )
	{
		case 0 :
			return 0;
		case 1 :
		case 2 :
			return 1;
		default :
			Cache &c = recursiveCache<Cache>();
			return c.get( key - 1 ) + c.get( key - 2 );
	}
}

template<typename Cache>
Cache &recursiveCache()
{
	static Cache c( getRecursive<Cache> );
	return c;
}

struct GetFromParallelRecursiveCache
{
	public :

		GetFromParallelRecursiveCache( ParallelTestCache &cache, size_t numValues )
			:	m_cache( cache ), m_numValues( numValues )
		{
		}

		void operator()( const blocked_range<size_t> &r ) const
		{
			for( size_t i=r.begin(); i!=r.end(); ++i )
			{
				m_cache.get( i % m_numValues );
			}
		}

	private :

		ParallelTestCache &m_cache;
		size_t m_numValues;

};

void testSerialLRUCacheRecursion( int maxCost )
{
	SerialTestCache &cache = recursiveCache<SerialTestCache>();
	cache.clear();
	cache.setMaxCost( maxCost );
	if( cache.get( 40 ) != 102334155 )
	{
		throw Exception( "Unexpected result" );
	}
}

void testParallelLRUCacheRecursion( int numIterations, size_t numValues, int maxCost )
{
	ParallelTestCache &cache = recursiveCache<ParallelTestCache>();
	cache.clear();
	cache.setMaxCost( maxCost );
	tbb::task_group_context taskGroupContext( tbb::task_group_context::isolated );
	parallel_for( blocked_range<size_t>( 0, numIterations ), GetFromParallelRecursiveCache( cache, numValues ), taskGroupContext );
}

} // namespace

void IECorePython::bindLRUCache()
{

	class_<PythonLRUCache, boost::noncopyable>( "LRUCache", no_init )
		.def( init<object, PythonLRUCache::Cost>( ( boost::python::arg_( "getter" ), boost::python::arg_( "maxCost" )=500  ) ) )
		.def( init<object, object, PythonLRUCache::Cost>( ( boost::python::arg_( "getter" ), boost::python::arg_( "removalCallback" ), boost::python::arg_( "maxCost" )  ) ) )
		.def( "clear", &PythonLRUCache::clear )
		.def( "erase", &PythonLRUCache::erase )
		.def( "setMaxCost", &PythonLRUCache::setMaxCost )
		.def( "getMaxCost", &PythonLRUCache::getMaxCost )
		.def( "currentCost", &PythonLRUCache::currentCost )
		.def( "get", &PythonLRUCache::get )
		.def( "set", &PythonLRUCache::set )
		.def( "cached", &PythonLRUCache::cached )
	;

	/// \todo If we create an IECoreTest module, move these into it.
	def(
		"testLRUCacheThreading",
		testLRUCacheThreading,
		(
			boost::python::arg( "numIterations" ),
			boost::python::arg( "numValues" ),
			boost::python::arg( "maxCost" ),
			boost::python::arg( "clearFrequency" ) = 0
		)
	);

	def( "testSerialLRUCacheRecursion", testSerialLRUCacheRecursion );
	def( "testParallelLRUCacheRecursion", testParallelLRUCacheRecursion );

}
