# From pre-branching point as Fedora
%define commit 997b3b5b9
%define commit_short %(echo %{commit} | head -c 5)

# ROSA has a lot of hardening flags, they break valgrind
# Valgrind also does not neeed -O2:
# -O2 doesn't work for the vgpreload libraries either. They are meant
# to not be optimized to show precisely what happened. valgrind adds
# -O2 itself wherever suitable.
# Filter -Wstrict-aliasing=2, leaving only -gdwarf-4
%global optflags %(echo %{debugcflags} | tr ' ' '\n' | grep -v strict-alias | tr '\n' ' ')
%global ldflags %{nil}
%global build_ldflags %{nil}

# (From Fedora, rpm4-specific)
# Generating minisymtabs doesn't really work for the staticly linked
# tools. Note (below) that we don't strip the vgpreload libraries at all
# because valgrind might read and need the debuginfo in those (client)
# libraries for better error reporting and sometimes correctly unwinding.
# So those will already have their full symbol table.
%undefine _include_minidebuginfo

# Whether to run the full regtest or only a limited set
# The full regtest includes gdb_server integration tests.
%define	run_full_regtest 0

# TODO: reenable openmpi when its buildability is fixed
%global build_openmpi 0
%global build_tools_devel 1

# Define valarch, the architecture name that valgrind uses
# And only_arch, the configure option to only build for that arch.
%ifarch %{ix86}
%define valarch x86
%define only_arch --enable-only32bit
%endif
%ifarch %{x86_64}
%define valarch amd64
%define only_arch --enable-only64bit
%endif
%ifarch ppc
%define valarch ppc32
%define only_arch --enable-only32bit
%endif
%ifarch ppc64
%define valarch ppc64be
%define only_arch --enable-only64bit
%endif
%ifarch ppc64le
%define valarch ppc64le
%define only_arch --enable-only64bit
%endif
%ifarch s390x
%define valarch s390x
%define only_arch --enable-only64bit
%endif
%ifarch armv7hnl
%define valarch arm
%define only_arch --enable-only32bit
%endif
%ifarch aarch64
%define valarch arm64
%define only_arch --enable-only64bit
%endif

%global debug_package %{nil}

Summary:	Tools for runtime analysis and debugging of software
Name:		valgrind
Version:	3.23.0
Release:	1
License:	GPLv2+
Group:		Development/Tools
Url:		https://valgrind.org/

# We could use %%valgrind_arches as defined in redhat-rpm-config
# But that is really for programs using valgrind, it defines the
# set of architectures that valgrind works correctly on.
ExclusiveArch: %{ix86} %{x86_64} ppc ppc64 ppc64le s390x %{armx}

# Packaged manually when building a git snapshot!
# git clone git://sourceware.org/git/valgrind.git
# cd valgrind
# git checkout %{commit}
# cd ..
# XZ_OPT='-T0' tar cJf "/tmp/valgrind-%{version}.tar.xz" --directory=. valgrind
Source0:	https://sourceware.org/pub/valgrind/%{name}-%{version}.tar.bz2
Source100:	%{name}.rpmlintrc

# From Fedora
# Note that not all patches from their sources are really applied

# Needs investigation and pushing upstream
Patch1:		valgrind-3.9.0-cachegrind-improvements.patch
# Make ld.so supressions slightly less specific.
Patch3:		valgrind-3.9.0-ldso-supp.patch
Patch10:	rbernon_930070c2d2a679ffe21fa8a97275256fbdf610c5.patch
Patch11:	rbernon_c3d01f523774228bbd3f34b2a783b043de01c035.patch
Patch12:	rbernon_0d262bd37e7ef9472c6b0f49c137dad5f80dae56.patch
Patch13:	rbernon_ba5db7de4e168161de6cd57a84bdc5e70657f4ff.patch
Patch14:	rbernon_73622f132d52db028bb65b08f43e1b88952199ab.patch
Patch15:	rbernon_75799f756b1002e52d2f50f1ac7806ef1cc6e4bc.patch

BuildRequires:	binutils
%ifarch %{aarch64}
BuildRequires:	gcc-c++
%endif
BuildRequires:	gdb
BuildRequires:	procps
BuildRequires:	glibc-static-devel
BuildRequires:	boost-devel
BuildRequires:	libgomp-devel
%if %{build_openmpi}
BuildRequires:	openmpi-devel
%endif
# for docs
BuildRequires:	/usr/bin/xsltproc
# for make -C docs print-docs
#BuildRequires:	/usr/bin/pdfxmltex
BuildRequires:	docbook-style-xsl
BuildRequires:	docbook-dtd-xml
BuildRequires:	docbook-dtd45-xml
BuildRequires:	sgml-common

%if %{run_full_regtest}
Requires:	gdb
%else
Recommends:	gdb
%endif
Provides:   valgrind-plugins = %{EVRD}
Obsoletes:	valgrind-plugins < 3.13.0
# FIXME this should really be a hard dependency, but we can't
# do that while abf unconditionally moves debuginfo packages to
# separate repositories
Suggests:	glibc-debuginfo

%description
Valgrind is an instrumentation framework for building dynamic analysis 
tools. You can also use it to build new tools.
There are tools that can automatically detect many memory management and
threading bugs, and profile programs in detail: the distribution currently
includes six production-quality tools: two thread error detectors (helgrind
and drd), a cache and branch-prediction profiler (cachegrind), a call-graph
generating cache and branch-prediction profiler (callgrind), a heap profiler
(massif) and a memory error detector (memcheck, the default tool).
This one can detect problems such as:
* accessing memory you shouldn't, e.g. overrunning and underrunning heap
blocks, overrunning the top of the stack, and accessing memory after it has 
been freed.

* Using undefined values, i.e. values that have not been initialised, or
that have been derived from other undefined values.

* Incorrect freeing of heap memory, such as double-freeing heap blocks,
or mismatched use of malloc/new/new[] versus free/delete/delete[].

* Overlapping src and dst pointers in memcpy and related functions.

* Memory leaks.

%files
%doc %{_defaultdocdir}/%{name}
%{_bindir}/*
%dir %{_libexecdir}/valgrind
# Install everything in the libdir except the .so.
# The vgpreload so files might need file mode adjustment.
%{_libexecdir}/valgrind/*[^o]
# Turn on executable bit again for vgpreload libraries.
# Was disabled in %%install to prevent debuginfo stripping.
%attr(0755,root,root) %{_libexecdir}/valgrind/vgpreload*-%{valarch}-*so
%{_mandir}/man1/*

#----------------------------------------------------------------------------

%package devel
Summary:	Development files for Valgrind
Group:		Development/Tools
Conflicts:	%{name} < 3.9.0
# compat with old packaging to avoid breaking BRs
%if %{build_tools_devel}
Requires:	%{name}-tools-devel = %{EVRD}
%endif

%description devel
Development files required to develop software using Valgrind.

%files devel
%dir %{_includedir}/valgrind
%{_includedir}/valgrind/valgrind.h
%{_includedir}/valgrind/cachegrind.h
%{_includedir}/valgrind/callgrind.h
%{_includedir}/valgrind/dhat.h
%{_includedir}/valgrind/drd.h
%{_includedir}/valgrind/helgrind.h
%{_includedir}/valgrind/memcheck.h
%{_libdir}/pkgconfig/valgrind.pc

#----------------------------------------------------------------------------

%if %{build_tools_devel}

%package tools-devel
Summary:	Development files for building valgrind tools
Group:		Development/Tools
Conflicts:	%{name} < 3.9.0

%description tools-devel
Header files and libraries for development of valgrind tools.

%files tools-devel
%{_includedir}/valgrind/config.h
%{_includedir}/valgrind/libvex*h
%{_includedir}/valgrind/pub_tool_*h
%{_includedir}/valgrind/vki
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.a

%endif

#----------------------------------------------------------------------------

%if %{build_openmpi}

%package openmpi
Summary: OpenMPI support for Valgrind
Requires: %{name} = %{EVRD}

%description openmpi
A wrapper library for debugging OpenMPI parallel programs with valgrind.
See the section on Debugging MPI Parallel Programs with Valgrind in the
Valgrind User Manual for details.

%files openmpi
%{_libdir}/openmpi/valgrind/libmpiwrap*.so
%{_libdir}/valgrind/libmpiwrap*.so

%endif

#----------------------------------------------------------------------------

%prep
%autosetup -p1

%build
# Some patches (might) touch Makefile.am or configure.ac files.
# Just always autoreconf so we don't need patches to prebuild files.
./autogen.sh

# We explicitly don't want the libmpi wrapper. So make sure that configure
# doesn't pick some random mpi compiler that happens to be installed.
%define mpiccpath /bin/false

%ifarch %{aarch64}
# Valgrind relies on __builtin_longjmp, which clang (as of 15.0)
# doesn't implement for aarch64
export CC=gcc
export CXX=g++
%endif

%configure \
  --with-mpicc=%{mpiccpath} \
  %{only_arch} \
  GDB=%{_bindir}/gdb
 
%make
make man-pages -C docs
make html-docs -C docs
make FAQ.txt -C docs
#make print-docs -C docs
 
%install
%make_install
%make_install install-data-hook -C docs
 
# We want the MPI wrapper installed under the openmpi libdir so the script
# generating the MPI library requires picks them up and sets up the right
# openmpi libmpi.so requires. Install symlinks in the original/upstream
# location for backwards compatibility.
%if %{build_openmpi}
pushd %{buildroot}%{_libdir}
mkdir -p openmpi/valgrind
cd valgrind
mv libmpiwrap-%{valarch}-linux.so ../openmpi/valgrind/
ln -s ../openmpi/valgrind/libmpiwrap-%{valarch}-linux.so
popd
%endif
 
%if %{build_tools_devel}
%ifarch %{ix86} %{x86_64}
# To avoid multilib clashes in between i?86 and x86_64,
# tweak installed <valgrind/config.h> a little bit.
for i in HAVE_PTHREAD_CREATE_GLIBC_2_0 HAVE_PTRACE_GETREGS HAVE_AS_AMD64_FXSAVE64; do
  sed -i -e 's,^\(#define '$i' 1\|/\* #undef '$i' \*/\)$,#ifdef __x86_64__\n# define '$i' 1\n#endif,' \
    %{buildroot}%{_includedir}/valgrind/config.h
done
%endif
%else
# Remove files we aren't going to package.
# See tools-devel files.
rm %{buildroot}%{_includedir}/valgrind/config.h
rm %{buildroot}%{_includedir}/valgrind/libvex*h
rm %{buildroot}%{_includedir}/valgrind/pub_tool_*h
rm -rf %{buildroot}%{_includedir}/valgrind/vki
rm %{buildroot}%{_libdir}/valgrind/*.a
%endif
 
# We don't want debuginfo generated for the vgpreload libraries.
# Turn off execute bit so they aren't included in the debuginfo.list.
# We'll turn the execute bit on again in %%files.
chmod 644 %{buildroot}%{_libexecdir}/valgrind/vgpreload*-%{valarch}-*so

%check
# Prepare a little program to ensure that there are no unexpected
# file descriptors open, the testsuite otherwise always fails.
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
%__cc %{optflags} -o close_fds close_fds.c

# ?
for i in `find . -type f \( -name *-amd64-linux -o -name *-x86-linux -o -name *-ppc*-linux \)`; do
  case "`file $i`" in
    *ELF*executable*statically\ linked*)
      objcopy -R .debug_loc -R .debug_frame -R .debug_ranges $i
  esac
done

# Make sure a basic binary runs. There should be no errors.
./vg-in-place --error-exitcode=1 /bin/true || :

# Make sure no extra CFLAGS, CXXFLAGS or LDFLAGS leak through,
# the testsuite sets all flags as necessary.
make CFLAGS="" CXXFLAGS="" LDFLAGS="" check || :

# Workaround https://bugzilla.redhat.com/show_bug.cgi?id=1434601
# for gdbserver tests.
export PYTHONCOERCECLOCALE=0

# some tests are known to fail,
# just check no more tests are failing than in Fedora ;)
echo ===============TESTING===================
%if %{run_full_regtest}
  ./close_fds make regtest || :
%else
  ./close_fds make nonexp-regtest || :
%endif

# Make sure test failures show up in build.log
# Gather up the diffs (at most the first 20 lines for each one)
MAX_LINES=20
diff_files=`find . -name '*.diff' | sort`
if [ z"$diff_files" = z ] ; then
	echo "Congratulations, all tests passed!" >> diffs
else
	for i in $diff_files ; do
		echo "=================================================" >> diffs
		echo $i                                                  >> diffs
		echo "=================================================" >> diffs
		if [ `wc -l < $i` -le $MAX_LINES ] ; then
			cat $i                                                >> diffs
		else
			head -n $MAX_LINES $i                                 >> diffs
			echo "<truncated beyond $MAX_LINES lines>"            >> diffs
		fi
	done
fi
cat diffs
echo ===============END TESTING===============
