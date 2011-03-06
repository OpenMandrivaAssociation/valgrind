%define _requires_exceptions GLIBC_PRIVATE

#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

# disable debug package, it can prevent valgrind for working properly
%define debug_package   %{nil}

Name: 		valgrind
Version:	3.6.1
Release:	%mkrel 1
Summary: 	Memory debugger
License: 	GPLv2+
Group: 		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
# (fc) 3.3.0-4mdv add cachegrind improvement (Fedora)
Patch0:		valgrind-3.4.1-cachegrind-improvements.patch
# (fc) 3.3.0-4mdv fix openat handling (RH bug #208097) (Fedora)
Patch1:		valgrind-3.3.0-openat.patch
# (proyvind): 3.4.1-3 add wildcards after GLIBC_VERSION to match any library
# micro versions as well (Fedora)
Patch2:		valgrind-3.4.1-glibc-2.10.1.patch
# http://cvs.fedoraproject.org/viewvc/F-12/valgrind/valgrind-3.5.0-glibc-2.11.patch
# sample of an "emergency" hack to build on an usupported (newer) glibc...
Patch3:		valgrind-3.5.0-glibc-2.11.patch

URL: 		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc
BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, boost & qt4 threads
BuildRequires:	libgomp-devel boost-devel qt4-devel
Suggests:	gdb
Obsoletes:	valgrind-plugins
BuildRoot: 	%{_tmppath}/%{name}-%{version}

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


%prep
%setup -q 
%patch0 -p1 -b .cachegrind-improvements~
%patch1 -p1 -b .openat~
%patch2 -p1 -b .glibc-2.10.1~
#%patch3 -p1 -b .glibc-2.11

%build
# required for qt4 thread support as configure script shipped with package were
# generated with either outdated or missing pkg-config
autoreconf
%configure2_5x

%make

%install
rm -rf %{buildroot}
# Don't strip (prevent valgrind from working properly, as explained in README_PACKAGERS)
export DONT_STRIP=1

# FIXME exporting DONT_STRIP=1 is causing some weird behavior with debug_package
# and causing it to not set DISABLE_DEBUG=1
export DISABLE_DEBUG=1
%makeinstall

#don't package generated files
rm -f $RPM_BUILD_ROOT%{_libdir}/valgrind/*.supp.in

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

make check || :
# some tests are known to fail,
# just check no more tests are failing than Fedora ;)
echo ===============TESTING===================
./close_fds make regtest || :
echo ===============END TESTING===============



%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README* AUTHORS FAQ.txt
%{_bindir}/*
%{_libdir}/%{name}
%{_includedir}/valgrind/
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man1/*.1*

