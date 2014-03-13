#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

# disable debug package, it can prevent valgrind for working properly
%define	debug_package	%{nil}

%bcond_without	qt4

Name:		valgrind
Version:	3.9.0
Release:	2
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

# On some ppc64 installs these test just hangs
Patch5:		valgrind-3.9.0-gdbserver_tests-mcinvoke-ppc64.patch

# KDE#326983 - insn_basic test might crash because of setting DF flag 
Patch6:		valgrind-3.9.0-amd64_gen_insn_test.patch

# KDE#327837 - dwz compressed alternate .debug_info/str not read correctly.
Patch7:		valgrind-3.9.0-dwz-alt-buildid.patch

# KDE#327284 - s390x VEX miscompilation of -march=z10 binary
Patch8:		valgrind-3.9.0-s390-risbg.patch

# KDE#327916 - DW_TAG_typedef may have no name
Patch9:		valgrind-3.9.0-anon-typedef.patch

# KDE#327943 - s390x missing index/strchr suppression for ld.so bad backtrace?
Patch10:	valgrind-3.9.0-s390x-ld-supp.patch

# KDE#328100 - XABORT not implemented
Patch11:	valgrind-3.9.0-xabort.patch

# KDE#328711 - valgrind.1 manpage "memcheck options" section is bad
Patch12:	valgrind-3.9.0-manpage-memcheck-options.patch

# KDE#328455 - s390x SIGILL after emitting wrong register pair for ldxbr
Patch13:	valgrind-3.9.0-s390-fpr-pair.patch

# KDE#331337 - s390x WARNING: unhandled syscall: 326 (dup3)
Patch14: valgrind-3.9.0-s390-dup3.patch

# KDE#331380 - Syscall param timer_create(evp) points to uninitialised byte(s)
Patch15: valgrind-3.9.0-timer_create.patch

# Accept glibc 2.19 as valid (upstream valgrind svn r13829)
Patch16: valgrind-3.9.0-glibc-2.19.patch

URL:		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc %{arm}
BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, boost & qt4 threads
BuildRequires:	gomp-devel boost-devel
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
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/default.supp
%{_libdir}/valgrind/*.so
%{_libdir}/valgrind/*-linux
%{_mandir}/man1/*.1*
%{_datadir}/valgrind/*.xml
%{_datadir}/valgrind/default.supp

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
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%ifarch s390x
%patch10 -p1
%endif

%patch11 -p1
%patch12 -p1
%patch13 -p1

%patch14 -p1
%patch15 -p1
%patch16 -p1

# These tests go into an endless loop on ARM
# There is a __sync_add_and_fetch in the testcase.
# DRD is doing this trace printing inside the loop
# which causes the reservation (LDREX) to fail so
# it can never make progress.
%ifarch %{arm}
rm -f drd/tests/annotate_trace_memory_xml.vgtest
rm -f drd/tests/annotate_trace_memory.vgtest
%endif

# rebuild unconditionally because we patch configure.in
autoreconf

%build
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
%{__cc} $RPM_OPT_FLAGS -o close_fds close_fds.c

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

