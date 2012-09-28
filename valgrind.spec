%define _requires_exceptions GLIBC_PRIVATE

#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

# disable debug package, it can prevent valgrind for working properly
%define debug_package   %{nil}

# (blino) FIXME: reenable qt4 as soon as availble in cauldron
%bcond_without	qt4

Name: 		valgrind
Version:	3.8.1
Release:	%mkrel 1
Summary: 	Memory debugger
License: 	GPLv2+
Group: 		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
# From Fedora:
Patch1:		valgrind-3.8.0-cachegrind-improvements.patch
Patch2:		valgrind-3.8.0-openat.patch
Patch3:		valgrind-3.8.0-helgrind-race-supp.patch
Patch4:		valgrind-3.8.0-stat_h.patch
Patch5:		valgrind-3.8.0-capget.patch
Patch6:		valgrind-3.8.0-pie.patch
Patch7:		valgrind-3.8.0-config_h.patch
Patch8:		valgrind-3.8.0-tests.patch
Patch9:		valgrind-3.8.0-enable-armv5.patch
Patch10:	valgrind-3.8.0-ldso-supp.patch
Patch11:	valgrind-3.8.0-x86-backtrace.patch
Patch12:	valgrind-3.8.0-find-buildid.patch

# https://bugs.kde.org/show_bug.cgi?id=305513
Patch102:	valgrind-fix-segv.diff

URL: 		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc
BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, boost & qt4 threads
BuildRequires:	libgomp-devel boost-devel
%if %{with qt4}
BuildRequires:	qt4-devel
%endif
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
%doc README* AUTHORS FAQ.txt
%{_bindir}/*
%{_libdir}/%{name}
%{_mandir}/man1/*.1*
%{_datadir}/valgrind/*.xml
%{_datadir}/valgrind/default.supp

#--------------------------------------------------------------------

%package	devel
Summary:	%{summary}
Group:		%{group}
Conflicts:	%{name} < 3.6.1-3

%description	devel
Development files required to develop software using valgrind.

%files devel
%dir %{_includedir}/valgrind
%{_includedir}/valgrind/*
%{_libdir}/pkgconfig/%{name}.pc

#--------------------------------------------------------------------

%prep
%setup -q
%apply_patches

%build

# Convert the library paths with /lib or /lib64 in the suppressions to those
# with /usr/lib or /usr/lib64 due to the /usrmove .
perl -pi -e 's!obj:/lib!obj:/usr/lib!g' *.supp *.supp.in

# (From Fedora):
# Filter out some flags that cause lots of valgrind test failures.
# Also filter away -O2, valgrind adds it wherever suitable, but
# not for tests which should be -O0, as they aren't meant to be
# compiled with -O2 unless explicitely requested.
export CFLAGS="`echo " %{optflags} " | sed 's/ -m\(64\|3[21]\) / /g;s/ -fexceptions / /g;s/ -fstack-protector / / g;s/ -Wp,-D_FORTIFY_SOURCE=2 / /g;s/-O2 / /g;s/^ //;s/ $//'`"

# filter out one more flag (unused in FC but causes faillure in mga3:
export CFLAGS="`echo " ${CFLAGS} " | sed -e 's/ -fPIC//'`"
# fix flags in other cases (CXXFLAGS, FFLAGS):
%define optflags $CFLAGS

# rebuild unconditionally because we patch configure.in
autoreconf
%configure2_5x

%make

%install
# Don't strip (prevent valgrind from working properly, as explained in README_PACKAGERS)
export DONT_STRIP=1

# FIXME exporting DONT_STRIP=1 is causing some weird behavior with debug_package
# and causing it to not set DISABLE_DEBUG=1
export DISABLE_DEBUG=1

%makeinstall

mkdir %buildroot/%_datadir/valgrind
mv  %buildroot/%_libdir/valgrind/*.{supp,xml} %buildroot/%_datadir/valgrind

# It's a kludge, but appears to get valgrind to work, because it looks for
# default.supp under %%{_libdir} instead of under %%{_datadir}, where it is
# now installed.
ln -sf %{_datadir}/valgrind/default.supp "$RPM_BUILD_ROOT"/%{_libdir}/valgrind/default.supp

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
# Cancel this temporarily because the tests hang on x86-64:
# http://thread.gmane.org/gmane.comp.debugging.valgrind/11792
# ./close_fds make regtest || :
echo ===============END TESTING===============

