%define	_filter_GLIBC_PRIVATE	1

#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

Name: 		valgrind
Version:	3.7.0
Release:	1
Summary: 	Memory debugger
License: 	GPLv2+
Group: 		Development/Other
# a855fda56edf05614f099dca316d1775
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
Patch1:		valgrind-3.7.0-cachegrind-improvements.patch
Patch2:		valgrind-3.7.0-openat.patch
Patch3:		valgrind-3.7.0-helgrind-race-supp.patch
Patch4:		valgrind-3.7.0-stat_h.patch
Patch5:		valgrind-3.7.0-capget.patch
Patch6:		valgrind-3.7.0-pie.patch
Patch7:		valgrind-3.7.0-gcc-version.patch
# Do not tell ebx is clobbered in exit syscall
# to avoid gcc error, as done in valgrind 3.6.1
Patch8:		valgrind-3.7.0-pic-clobber.patch

URL: 		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc
BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, boost & qt4 threads
BuildRequires:	libgomp-devel boost-devel qt4-devel
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

%package	devel
Summary:	%{summary}
Group:		%{group}

%description	devel
Development files required to develop software using valgrind.

%prep
%setup -q 
%apply_patches

# required for qt4 thread support as configure script shipped with package were
# generated with either outdated or missing pkg-config
autoreconf

%build
%configure
%make

%install
export EXCLUDE_FROM_STRIP=%{_libdir}/valgrind/*.so
%makeinstall

#don't package generated files
rm -f %{buildroot}%{_libdir}/valgrind/*.supp.in

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
gcc $RPM_OPT_FLAGS -o close_fds close_fds.c

for i in `find . -type f \( -name *-amd64-linux -o -name *-x86-linux -o -name *-ppc*-linux \)`; do
  case "`file $i`" in
    *ELF*executable*statically\ linked*)
      objcopy -R .debug_loc -R .debug_frame -R .debug_ranges $i
  esac
done

# Some tests have issues with non volatile global variables accessed
# by multiple threads on i586, and also in i586, some tests fail due
# to not being able to modify running testcase variables in the
# gdb server interface, and then looping forever e.g. sleepers test.
make CFLAGS="-O0 -g3" CXXFLAGS="-O0 -g3" check || :
# some tests are known to fail,
# just check no more tests are failing than Fedora ;)
echo ===============TESTING===================
./close_fds make regtest || :
echo ===============END TESTING===============

%files
%doc README* AUTHORS FAQ.txt
%{_bindir}/*
%{_libdir}/%{name}
%{_mandir}/man1/*.1*

%files devel
%dir %{_includedir}/valgrind
%{_includedir}/valgrind/*
%{_libdir}/pkgconfig/%{name}.pc
