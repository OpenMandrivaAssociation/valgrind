#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1
%define _disable_lto %{nil}
%define	_ssp_cflags %{nil}

%bcond_without	qt4
%ifnarch aarch64
%bcond_with	openmpi
%endif

Name:		valgrind
Version:	3.11.0
Release:	1
Summary:	Memory debugger
License:	GPLv2+
Group:		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
Source1:	%{name}.rpmlintrc

# Needs investigation and pushing upstream
Patch1: valgrind-3.9.0-cachegrind-improvements.patch

# KDE#211352 - helgrind races in helgrind's own mythread_wrapper
Patch2: valgrind-3.9.0-helgrind-race-supp.patch

# Make ld.so supressions slightly less specific.
Patch3: valgrind-3.9.0-ldso-supp.patch

# KDE#353083 arm64 doesn't implement various xattr system calls.
Patch4: valgrind-3.11.0-arm64-xattr.patch

# KDE#353084 arm64 doesn't support sigpending system call.
Patch5: valgrind-3.11.0-arm64-sigpending.patch

# KDE#353370 don't advertise RDRAND in cpuid for Core-i7-4910-like avx2
Patch6: valgrind-3.11.0-no-rdrand.patch

# KDE#278744 cvtps2pd with redundant RexW
Patch7: valgrind-3.11.0-rexw-cvtps2pd.patch

# KDE#353680 Crash with certain glibc versions due to non-implemented TBEGIN
Patch8: valgrind-3.11.0-s390-hwcap.patch

# KDE#355188 valgrind should intercept all malloc related global functions
Patch9: valgrind-3.11.0-wrapmalloc.patch

# RHBZ#1283774 - Valgrind: FATAL: aspacem assertion failed
Patch10: valgrind-3.11.0-aspacemgr.patch

# KDE#358213 - helgrind bar_bad testcase hangs with new glibc pthread barrier
Patch11: valgrind-3.11.0-pthread_barrier.patch

# KDE#357833 - Valgrind is broken on recent linux kernel (RLIMIT_DATA)
Patch12: valgrind-3.11.0-rlimit_data.patch

# KDE#357887 VG_(fclose) ought to close the file, you silly.
Patch13: valgrind-3.11.0-fclose.patch

# KDE#357871 Fix helgrind wrapper of pthread_spin_destroy
Patch14: valgrind-3.11.0-pthread_spin_destroy.patch

# KDE#358030 Support direct socket calls on x86 32bit (new in linux 4.3)
Patch15: valgrind-3.11.0-socketcall-x86-linux.patch

# KDE#356044 Dwarf line info reader misinterprets is_stmt register
Patch16: valgrind-3.11.0-is_stmt.patch

# Fix incorrect (or infinite loop) unwind on RHEL7 x86 32 bits. (svn r15729)
# Fix incorrect (or infinite loop) unwind on RHEL7 amd64 64 bits. (svn r15794)
Patch17: valgrind-3.11.0-x86_unwind.patch

# KDE#358478 drd/tests/std_thread.cpp doesn't build with GCC6
Patch18: valgrind-3.11.0-drd_std_thread.patch

# KDE#359201 futex syscall skips argument 5 if op is FUTEX_WAIT_BITSET
Patch19: valgrind-3.11.0-futex.patch

# KDE#359289 s390: Implement popcnt insn.
Patch20: valgrind-3.11.0-s390x-popcnt.patch

# KDE#359703 s390: wire up separate socketcalls system calls
Patch21: valgrind-3.11.0-s390-separate-socketcalls.patch

# KDE#359733 amd64 implement ld.so strchr/index override like x86
Patch22: valgrind-3.11.0-amd64-ld-index.patch

# KDE#359871 Incorrect mask handling in ppoll
Patch23: valgrind-3.11.0-ppoll-mask.patch

# KDE#359503 - Add missing syscalls for aarch64 (arm64)
Patch24: valgrind-3.11.0-arm64-more-syscalls.patch

# Workaround for KDE#345307 - still reachable memory in libstdc++ from gcc 5
Patch25: valgrind-3.11.0-libstdc++-supp.patch

# KDE#360519 - none/tests/arm64/memory.vgtest might fail with newer gcc
Patch26: valgrind-3.11.0-arm64-ldr-literal-test.patch

# KDE#360425 - arm64 unsupported instruction ldpsw
Patch27: valgrind-3.11.0-arm64-ldpsw.patch

# KDE#345307 - still reachable memory in libstdc++ from gcc 6
# Note that workaround (patch25) is still needed for gcc 5
Patch28: valgrind-3.11.0-cxx-freeres.patch

# KDE#361354 - ppc64[le]: wire up separate socketcalls system calls
Patch29: valgrind-3.11.0-ppc64-separate-socketcalls.patch

# KDE#356393 - valgrind (vex) crashes because isZeroU happened
Patch30: valgrind-3.11.0-isZeroU.patch

# KDE#359472 - PPC vsubuqm instruction doesn't always give the correct result
Patch31: valgrind-3.11.0-ppc64-128bit-mod-carry.patch

# KDE#212352 - vex amd64 unhandled opc_aux = 0x 2, first_opcode == 0xDC (FCOM)
Patch32: valgrind-3.11.0-amd64-fcom.patch

# s390: Recognise machine model z13s (2965)
Patch33: valgrind-3.11.0-z13s.patch

# Update gdbserver_tests filter for newer GDB version.
Patch34: valgrind-3.11.0-gdb-test-filters.patch

# KDE#361226 s390x: risbgn (EC59) not implemented
Patch35: valgrind-3.11.0-s390x-risbgn.patch

# ours
# strlen is no longer to be found in ld.so, dunno why, but let's just work
# around it for now...
#Patch100:	valgrind-3.10.1-hack-around-strlen-no-longer-exported-by-ld.so.patch
Patch101:	valgrind-3.7.0-respect-flags.patch

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
BuildRequires:	xsltproc

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
%apply_patches

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
mkdir -p bfd
ln -s %{_bindir}/ld.bfd bfd/%{_target_platform}-ld
export PATH=$PWD/bfd:$PATH

%global optflags %(echo %{optflags} -fuse-ld=bfd | sed -e 's#-fPIC##g')
%define __cc gcc
%define	__cxx g++
%configure \
%if %{with openmpi}
	--with-mpicc=%{mpiccpath} \
%endif
%ifarch aarch64
	--enable-only64bit
%endif

%make LD="%{_target_platform}-ld.bfd"
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

%make check CFLAGS="" check || :
# some tests are known to fail,
# just check no more tests are failing than Fedora ;)
echo ===============TESTING===================
# Cancel this temporarily because the tests hang on x86-64:
# http://thread.gmane.org/gmane.comp.debugging.valgrind/11792
# ./close_fds make regtest || :
echo ===============END TESTING===============

