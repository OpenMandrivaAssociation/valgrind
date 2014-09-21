#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

%bcond_without	qt4
%ifnarch aarch64
%bcond_with	openmpi
%endif

Name:		valgrind
Version:	3.10.0
Release:	1
Summary:	Memory debugger
License:	GPLv2+
Group:		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
Source1:	%{name}.rpmlintrc
# From Fedora:
# Needs investigation and pushing upstream
Patch1:		valgrind-3.9.0-cachegrind-improvements.patch

# KDE#211352 - helgrind races in helgrind's own mythread_wrapper
Patch2:		valgrind-3.9.0-helgrind-race-supp.patch

# undef st_atime, st_mtime and st_ctime. Unknown why this is (still?) needed.
Patch3:		valgrind-3.9.0-stat_h.patch

# Make ld.so supressions slightly less specific.
Patch4:		valgrind-3.9.0-ldso-supp.patch

URL:		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc %{armx}
BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, openmpi, boost & qt4 threads
BuildRequires:	gomp-devel boost-devel
%if %{with openmpi}
BuildRequires:	openmpi-devel
%endif
%if %{with qt4}
BuildRequires:	qt4-devel
%endif
BuildRequires:	docbook-style-xsl
Suggests:	gdb
Obsoletes:	valgrind-plugins

%description
When a program is run under Valgrind's supervision, all reads and
writes of memory are checked, and calls to malloc/new/free/delete are
intercepted. As a result, Valgrind can detect problems such as:

    * Use of uninitialised memory
    * Reading/writing memory after it has been free'd
    * Reading/writing off the end of malloc'd blocks
    * Reading/writing inappropriate areas on the stack
    * Memory leaks -- where pointers to malloc'd blocks are lost forever
    * Passing of uninitialised and/or unaddressible memory to system calls
    * Mismatched use of malloc/new/new [] vs free/delete/delete []

%files
%doc README* AUTHORS
%{_bindir}/*
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.so
%{_libdir}/valgrind/*-linux
%{_libdir}/valgrind/*.xml
%{_libdir}/valgrind/*.supp
%{_mandir}/man1/*.1*

#--------------------------------------------------------------------

%package	devel
Summary:	%{summary}
Group:		Development/Other
Conflicts:	%{name} < 3.6.1-3

%description	devel
Development files required to develop software using valgrind.

%files devel
%dir %{_includedir}/valgrind
%{_includedir}/valgrind/*
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/valgrind/*.a

#--------------------------------------------------------------------

%prep
%setup -q

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# These tests go into an endless loop on ARM
# There is a __sync_add_and_fetch in the testcase.
# DRD is doing this trace printing inside the loop
# which causes the reservation (LDREX) to fail so
# it can never make progress.
%ifarch %{arm}
rm drd/tests/annotate_trace_memory_xml.vgtest
rm drd/tests/annotate_trace_memory.vgtest
%endif

# rebuild unconditionally because we patch configure.in
autoreconf

%build
%global optflags %(echo %{optflags} | sed -e 's#-fPIC##g')
%configure2_5x \
%if %{with openmpi}
	--with-mpicc=%{mpiccpath} \
%endif
%ifarch aarch64
	--enable-only64bit
%endif

%make
# no idea why it doesn't automatically build these..
%make -C docs man-pages

%install
export EXCLUDE_FROM_STRIP=%{_libdir}/valgrind

%makeinstall_std
%makeinstall_std -C docs

%check
# Ensure there are no unexpected file descriptors open,
# the testsuite otherwise fails.
cat > close_fds.c <<EOF
#include <stdlib.h>
#include <unistd.h>
int main (int argc, char *const argv[])
{
  int i, j = sysconf (_SC_OPEN_MAX);
  if (j < 0)
    exit (1);
  for (i = 3; i < j; ++i)
    close (i);
  execvp (argv[1], argv + 1);
  exit (1);
}
EOF
%{__cc} $RPM_OPT_FLAGS -o close_fds close_fds.c

for i in `find . -type f \( -name *-amd64-linux -o -name *-x86-linux -o -name *-ppc*-linux \)`; do
  case "`file $i`" in
    *ELF*executable*statically\ linked*)
      objcopy -R .debug_loc -R .debug_frame -R .debug_ranges $i
  esac
done

sed -e 's#-gdwarf-4##g' -i memcheck/tests/Makefile

%make check
# some tests are known to fail,
# just check no more tests are failing than Fedora ;)
echo ===============TESTING===================
# Cancel this temporarily because the tests hang on x86-64:
# http://thread.gmane.org/gmane.comp.debugging.valgrind/11792
# ./close_fds make regtest || :
echo ===============END TESTING===============

