# Setting initial dist defaults.  Do not modify these.
# Note: Mock sets these up... but we need to default for manual builds.
%{!?el3:%define el3 0}
%{!?el4:%define el4 0}
%{!?el5:%define el5 0}
%{!?rhel:%define rhel 'empty'}

# Build Options
#
# In order to properly build you will likely need to add one of the following
# build options:
#
#       --with el3
#       --with el4
#       --with el5
#
#
# Note for maintainers/builders: mock handles all these defs.  We include them 
# here for manual builds.
#
%{?_with_el3:%define el3 1}
%{?_with_el3:%define rhel 3}
%{?_with_el3:%define dist .el3}

%{?_with_el4:%define el4 1}
%{?_with_el4:%define rhel 4}
%{?_with_el4:%define dist .el4}

%{?_with_el5:%define el5 1}
%{?_with_el5:%define rhel 5}
%{?_with_el5:%define dist .el5}

Name: mysqlclient16
Version: 5.1.61
Release: 2.ius%{?dist}
Summary: Backlevel MySQL shared libraries.
License: GPL
Group: Applications/Databases
URL: http://www.mysql.com

Source0: http://dev.mysql.com/get/Downloads/MySQL-4.1/mysql-%{version}.tar.gz
Source4: scriptstub.c
Source5: my_config.h

#Patch201: mysql-5.0.27-libdir.patch
#Patch2: mysql-errno.patch
#Patch303: mysql-5.0.33-libtool.patch
#Patch304: mysql-5.0.37-testing.patch
#Patch205: mysql-5.0.27-no-atomic.patch
#Patch6: mysql-rpl_ddl.patch
#Patch7: mysql-rpl-test.patch
#Patch207: mysql-5.0.41-compress-test.patch
#Patch208: mysql-5.0.67-mysqld_safe.patch
#Patch209: mysql-5.0.67-bindir.patch
#Patch217: mysql-5.0.75-automake_el3.patch

Patch1: mysql-ssl-multilib.patch
Patch2: mysql-errno.patch
# Patch3: mysql-stack.patch
Patch4: mysql-testing.patch
#Patch5: mysql-install-test.patch
Patch6: mysql-stack-guard.patch
#Patch7: mysql-plugin-bug.patch
Patch8: mysql-setschedparam.patch
#Patch10: mysql-strmov.patch
Patch11: mysql-signal-align.patch
Patch12: mysql-cve-2008-7247.patch
#Patch13: mysql-expired-certs.patch
#Patch14: mysql-charset-bug.patch
Patch15: mysql-no-docs.patch
#Patch16: mysql-lowercase-bug.patch

Patch201: mysql-5.1.24-libdir.patch
#Patch207: mysql-5.0.41-compress-test.patch 
Patch209: mysql-5.0.67-bindir.patch
Patch311: mysql-5.1.28-rc-mysqld_safe.patch
Patch315: mysql-5.1.37-sysconfig.patch
Patch316: mysql-5.1.61-disabled_tests.patch
# https://bugs.launchpad.net/ius/+bug/942524
Patch317: mysql-strmov.patch 
#update FSF address
Patch500: mysql.m4.patch


BuildRoot: %{_tmppath}/%{name}-%{version}-root
Prereq: /sbin/ldconfig, /sbin/install-info, grep, fileutils, chkconfig
BuildRequires: gperf, perl, readline-devel, openssl-devel
BuildRequires: gcc-c++, ncurses-devel, zlib-devel
BuildRequires: libtool automake autoconf gcc
Requires: bash
Provides: libmysqlclient.so.16   libmysqlclient.so.16.0.0 
Provides: libmysqlclient_r.so.16 libmysqlclient_r.so.16.0.0

%if %{el5}
BuildRequires: libpcap
Requires: libpcap
%endif

%if %{el3}
BuildRequires: gettext
%else
BuildRequires: gettext-devel
%endif


# Working around perl dependency checking bug in rpm FTTB. Remove later.
%define __perl_requires %{SOURCE999}

# Force include and library files into a nonstandard place
%{expand: %%define _origincludedir %{_includedir}}
%{expand: %%define _origlibdir %{_libdir}}
%define _includedir %{_origincludedir}/mysql5
%define _libdir %{_origlibdir}/mysql5

%description
This package contains backlevel versions of the MySQL client libraries
for use with applications linked against them.  These shared libraries
were created using MySQL %{version}.

%package devel

Summary: Backlevel files for development of MySQL applications.
License: GPL
Group: Applications/Databases
Requires: %{name} = %{version}-%{release}

%description devel
This package contains the libraries and header files that are needed for
developing MySQL applications using backlevel client libraries.

%prep
%setup -q -n mysql-%{version}

#%patch201 -p1
#%patch2 -p1
#%patch303 -p1
#%patch304 -p1
#%patch205 -p1
#%patch6 -p1
#%patch7 -p1
#%patch207 -p1
#%patch208 -p1
#%patch209 -p1
#%patch217 -p1 -b .openssl

%patch1 -p1
%patch2 -p1
# %%patch3 -p1
%patch4 -p1
#%%patch5 -p1
%patch6 -p1
#%%patch7 -p1
%patch8 -p1
#%patch10 -p1
%patch11 -p1
%patch12 -p1
#%%patch13 -p1
#%%patch14 -p1
%patch15 -p1
#%patch16 -p1
%patch201 -p1
#%%patch207 -p1  
%patch209 -p1 -b .bindir
%patch311 -p1 -b .mysqld_safe
%patch315 -p1 -b .sysconfig
%patch316 -p1 -b .disabled_tests
%patch317 -p1 -b .strmov
%patch500 -p1

## Work around for missing mkinstalldirs 
#if [ ! -e mkinstalldirs ]; then
#  cp -a /usr/share/gettext/mkinstalldirs mkinstalldirs
#  chmod +x mkinstalldirs
#fi

libtoolize --force
aclocal
automake

# This is a hack to fix autoconf issues on Rhel3
%if %{el3}
echo "ifdef([m4_pattern_allow], [m4_pattern_allow([AS_HELP_STRING])])" >> aclocal.m4
%endif

autoconf
autoheader

%build
CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE"
%if %{el3}
CFLAGS="$CFLAGS -fno-strict-aliasing"
%else
CFLAGS="$CFLAGS -fno-strict-aliasing -fwrapv"
%endif

# Also Resolved MySQL Bug: #18091 and #19999
# same as MySQL builds... always build as
# position indipendant code.
CFLAGS="$CFLAGS -fPIC"

CXXFLAGS="$CFLAGS  -felide-constructors -fno-rtti -fno-exceptions"
export CFLAGS CXXFLAGS

%configure \
	--with-readline \
	--with-vio \
	--with-ssl \
	--without-debug \
	--enable-shared \
	--without-bench \
	--localstatedir=/var/lib/mysql \
	--with-unix-socket-path=/var/lib/mysql/mysql.sock \
	--with-mysqld-user="mysql" \
	--with-extra-charsets=all \
	--enable-local-infile \
	--enable-large-files=yes --enable-largefile=yes \
	--enable-thread-safe-client \
	--disable-dependency-tracking \
	--with-archive-storage-engine \
	--with-federated-storage-engine \
	--with-blackhole-storage-engine \
	--with-csv-storage-engine \
	--with-named-thread-libs="-lpthread"

gcc $CFLAGS $LDFLAGS -o scriptstub "-DLIBDIR=\"%{_libdir}/mysql\"" %{SOURCE4}

make %{?_smp_mflags}
make check

%install
rm -rf %{buildroot}

%makeinstall

install -m 644 include/my_config.h %{buildroot}%{_includedir}/mysql/my_config_`uname -i`.h
install -m 644 %{SOURCE5} %{buildroot}%{_includedir}/mysql/

mv %{buildroot}%{_bindir}/mysqlbug %{buildroot}%{_libdir}/mysql/mysqlbug
install -m 0755 scriptstub %{buildroot}%{_bindir}/mysqlbug
mv %{buildroot}%{_bindir}/mysql_config %{buildroot}%{_libdir}/mysql/mysql_config
install -m 0755 scriptstub %{buildroot}%{_bindir}/mysql_config

# We want the .so files both in regular _libdir (for execution) and
# in special _libdir/mysql5 directory (for convenient building of clients).
# The ones in the latter directory should be just symlinks though.
mkdir -p %{buildroot}%{_origlibdir}/mysql
pushd %{buildroot}%{_origlibdir}/mysql
mv -f %{buildroot}%{_libdir}/mysql/libmysqlclient.so.16.*.* .
mv -f %{buildroot}%{_libdir}/mysql/libmysqlclient_r.so.16.*.* .
cp -p -d %{buildroot}%{_libdir}/mysql/libmysqlclient*.so.* .
popd
pushd %{buildroot}%{_libdir}/mysql
ln -s ../../mysql/libmysqlclient.so.16.*.* .
ln -s ../../mysql/libmysqlclient_r.so.16.*.* .
popd

# Put the config script into special libdir
cp -p %{buildroot}%{_bindir}/mysql_config %{buildroot}%{_libdir}/mysql

rm -rf %{buildroot}%{_prefix}/mysql-test
rm -f %{buildroot}%{_libdir}/mysql/*.a
rm -f %{buildroot}%{_libdir}/mysql/*.la
rm -rf %{buildroot}%{_datadir}/mysql
rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_libexecdir}
rm -rf %{buildroot}%{_infodir}/*
rm -rf %{buildroot}%{_mandir}/man1/*
rm -rf %{buildroot}%{_mandir}/man8/*
rm -f %{buildroot}%{_origlibdir}/mysql5/mysql/libmysqlclient.so
rm -f %{buildroot}%{_origlibdir}/mysql5/mysql/libmysqlclient_r.so
rm -f %{buildroot}%{_origlibdir}/mysql5/mysql/libndbclient.so
rm -f %{buildroot}%{_origlibdir}/mysql5/mysql/libndbclient.so.3

mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_origlibdir}/mysql" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf

%clean
rm -rf %{buildroot}

%post 
%if %{el3}
  if ! grep '^%{_libdir}/mysql$' /etc/ld.so.conf > /dev/null 2>&1
  then
    echo "%{_libdir}/mysql" >> /etc/ld.so.conf
  fi
%endif
/sbin/ldconfig


%postun
if [ $1 = 0 ] ; then
  %if %{el3}
    if grep '^%{_libdir}/mysql$' /etc/ld.so.conf > /dev/null 2>&1
    then
        grep -v '^%{_libdir}/mysql$' /etc/ld.so.conf \
            > /etc/ld.so.conf.$$ 2> /dev/null
        mv /etc/ld.so.conf.$$ /etc/ld.so.conf
    fi
  %endif
  /sbin/ldconfig
fi

%files
%defattr(-,root,root)
%doc README COPYING
%{_origlibdir}/mysql5/mysql/mysqlbug
%{_origlibdir}/mysql5/mysql/plugin
%{_origlibdir}/mysql/libmysqlclient*16*
%{_origlibdir}/mysql5/mysql/libmysqlclient*16*
%{_origlibdir}/mysql5/mysql/mysql_config
%{_prefix}/sql-bench/
%{_datarootdir}/aclocal/mysql.m4
/etc/ld.so.conf.d/mysqlclient16-*.conf 

%files devel
%defattr(-,root,root)
%{_includedir}/mysql/*.h

%changelog
* Wed Aug 21 2013 Ben Harper <ben.harper@rackspace.com> - 5.1.61-2.ius
- Patch500 added to match changes in mysql55

* Tue Mar 06 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 5.1.61-1.ius
- Latest sources from upstream
- Adding patch mysql-strmov.patch to address
  https://bugs.launchpad.net/ius/+bug/942524

* Mon Mar 21 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 5.1.56-1.ius
- New Package built off of the mysqlclient15 SPEC

