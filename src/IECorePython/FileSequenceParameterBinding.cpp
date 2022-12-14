//////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2009-2010, Image Engine Design Inc. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//   * Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//
//   * Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//
//   * Neither the name of Image Engine Design nor the names of any
//    other contributors to this software may be used to endorse or
//    promote products derived from this software without specific prior
//    written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "boost/python.hpp"

#include "IECorePython/FileSequenceParameterBinding.h"

#include "IECorePython/IECoreBinding.h"
#include "IECorePython/ParameterBinding.h"

#include "IECore/CompoundObject.h"
#include "IECore/Exception.h"
#include "IECore/FileSequenceParameter.h"

#include "boost/tokenizer.hpp"

using namespace boost::python;
using namespace IECore;
using namespace IECorePython;

namespace
{

class FileSequenceParameterWrapper : public ParameterWrapper<FileSequenceParameter>
{
	public:

		static FileSequenceParameter::ExtensionList makeExtensions( object extensions )
		{
			FileSequenceParameter::ExtensionList result;

			extract<list> eeList( extensions );
			if ( eeList.check() )
			{
				list ext = eeList();

				for ( long i = 0; i < IECorePython::len( ext ); i++ )
				{
					extract< std::string > ex( ext[i] );
					if ( !ex.check() )
					{
						throw InvalidArgumentException( "FileSequenceParameter: Invalid extensions value" );
					}

					result.push_back( ex() );
				}

			}
			else
			{
				extract<std::string> eeString( extensions );
				if ( eeString.check() )
				{
					std::string ext = eeString();
					boost::tokenizer< boost::char_separator<char> > t( ext, boost::char_separator<char>( " " ) );

					for ( boost::tokenizer<boost::char_separator<char> >::const_iterator it = t.begin(); it != t.end(); ++it )
					{
						result.push_back( *it );
					}
				}
				else
				{
					throw InvalidArgumentException( "FileSequenceParameter: Invalid extensions value" );
				}
			}

			return result;
		}

		/// Allow construction from either a string, StringData, or a FileSequence
		static std::string makeDefault( object defaultValue )
		{
			extract<std::string> deString( defaultValue );
			if( deString.check() )
			{
				return deString();
			}
			else
			{
				extract<StringData *> deStringData( defaultValue );
				if( deStringData.check() )
				{
					return deStringData()->readable();
				}
				else
				{
					extract<FileSequence *> deFileSequence( defaultValue );
					if( deFileSequence.check() )
					{
						return deFileSequence()->asString();
					}
					else
					{
						throw InvalidArgumentException( "FileSequenceParameter: Invalid default value" );
					}
				}
			}
		}

	public :

		FileSequenceParameterWrapper( PyObject *wrapperSelf, const std::string &n, const std::string &d, object dv = object( std::string("") ), bool allowEmptyString = true, FileSequenceParameter::CheckType check = FileSequenceParameter::DontCare, const object &p = boost::python::tuple(), bool po = false, CompoundObjectPtr ud = nullptr, object extensions = list(), size_t minSequenceSize = 2 )
			: ParameterWrapper<FileSequenceParameter>( wrapperSelf, n, d, makeDefault( dv ), allowEmptyString, check, parameterPresets<FileSequenceParameter::PresetsContainer>( p ), po, ud, makeExtensions( extensions ), minSequenceSize )
		{
		};

};

static list getFileSequenceExtensionsWrap( FileSequenceParameter &param )
{
	FileSequenceParameter::ExtensionList extensions = param.getExtensions();

	list result;
	for ( FileSequenceParameter::ExtensionList::const_iterator it = extensions.begin(); it != extensions.end(); ++it )
	{
		result.append( *it );
	}

	return result;
}

static void setFileSequenceExtensionsWrap( FileSequenceParameter &param, object ext )
{
	for ( long i = 0; i < IECorePython::len( ext ); i++)
	{
		param.setExtensions( FileSequenceParameterWrapper::makeExtensions( ext ) );
	}
}

} // namespace

namespace IECorePython
{

void bindFileSequenceParameter()
{
	FileSequencePtr (FileSequenceParameter::*getFileSequenceValueInternalData)() const = &FileSequenceParameter::getFileSequenceValue;
	FileSequencePtr (FileSequenceParameter::*getFileSequenceValueStringData)( const StringData *value ) const = &FileSequenceParameter::getFileSequenceValue;

	ParameterClass<FileSequenceParameter, FileSequenceParameterWrapper>()
		.def(
			init< const std::string &, const std::string &, boost::python::optional< object, bool, FileSequenceParameter::CheckType, const object &, bool, CompoundObjectPtr, object, int > >
			(
				(
					arg( "name" ),
					arg( "description" ),
					arg( "defaultValue" ) = object( std::string("") ),
					arg( "allowEmptyString" ) = true,
					arg( "check" ) = FileSequenceParameter::DontCare,
					arg( "presets" ) = boost::python::tuple(),
					arg( "presetsOnly" ) = false ,
					arg( "userData" ) = CompoundObject::Ptr( nullptr ),
					arg( "extensions" ) = list(),
					arg( "minSequenceSize" ) = 2
				)
			)
		)
		.def( "getFileSequenceValue", getFileSequenceValueInternalData )
		.def( "getFileSequenceValue", getFileSequenceValueStringData )
		.def( "setFileSequenceValue", &FileSequenceParameter::setFileSequenceValue )
		.def( "setMinSequenceSize", &FileSequenceParameter::setMinSequenceSize )
		.def( "getMinSequenceSize", &FileSequenceParameter::getMinSequenceSize )
		.add_property( "extensions",&getFileSequenceExtensionsWrap, &setFileSequenceExtensionsWrap )
	;

}

} // namespace IECorePython
