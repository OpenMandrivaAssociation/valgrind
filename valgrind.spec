#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

# disable debug package, it can prevent valgrind for working properly
%define debug_package   %{nil}

%bcond_without	qt4

Name: 		valgrind
Version:	3.8.1
Release:	3
Summary: 	Memory debugger
License: 	GPLv2+
Group: 		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
# From Fedora:
Patch1:		valgrind-3.8.1-cachegrind-improvements.patch

# KDE#307103 - sys_openat If pathname is absolute, then dirfd is ignored.
Patch2:		valgrind-3.8.1-openat.patch

# KDE#211352 - helgrind races in helgrind's own mythread_wrapper
Patch3:		valgrind-3.8.1-helgrind-race-supp.patch

Patch4:		valgrind-3.8.1-stat_h.patch

# Support really ancient gcc. Check __GNUC__ >= 3 for __builtin_expect.
Patch5:		valgrind-3.8.1-config_h.patch

# KDE#307101 - sys_capget second argument can be NULL 
Patch6:		valgrind-3.8.1-capget.patch

# KDE#263034 - Crash when loading some PPC64 binaries 
Patch7:		valgrind-3.8.1-pie.patch

# configure detection change from armv7* to armv[57]*.
Patch8:		valgrind-3.8.1-enable-armv5.patch

Patch9:		valgrind-3.8.1-ldso-supp.patch

# On x86 GCC 4.6 and later now defaults to -fomit-frame-pointer
# together with emitting unwind info (-fasynchronous-unwind-tables).
# So, try CF info first.
Patch10:	valgrind-3.8.1-x86-backtrace.patch

# KDE#305431 - Use find_buildid shdr fallback for separate .debug files
Patch11:	valgrind-3.8.1-find-buildid.patch

# KDE#305513 - Fix readdwarf.c read_unitinfo_dwarf2 abbrev reading
Patch12:	valgrind-3.8.1-abbrev-parsing.patch

# KDE#307038 - DWARF2 CFI reader: unhandled DW_OP_ opcode 0x8 (DW_OP_const1u) 
Patch13:	valgrind-3.8.1-cfi_dw_ops.patch

# On some ppc64 installs these test just hangs
Patch14:	valgrind-3.8.1-gdbserver_tests-mcinvoke-ppc64.patch

# KDE#307285 - x86_amd64 feature test for avx in test suite is wrong
# Should test OSXSAVE first before executing XGETBV.
Patch15:	valgrind-3.8.1-x86_amd64_features-avx.patch

# KDE#307155 - gdbserver_tests/filter_gdb should filter out syscall-template.S
# This is only a real issue when glibc-debuginfo is installed.
Patch16:	valgrind-3.8.1-gdbserver_tests-syscall-template-source.patch

# KDE#307290 - memcheck overlap testcase needs memcpy version filter
Patch17:	valgrind-3.8.1-overlap_memcpy_filter.patch
# Note: Need to make memcheck/tests/filter_memcpy executable

# KDE#307729 - pkgconfig support broken valgrind.pc
# valt_load_address=@VALT_LOAD_ADDRESS@
Patch18:	valgrind-3.8.1-pkg-config.patch

# KDE#253519 - Memcheck reports auxv pointer accesses as invalid reads. 
Patch19:	valgrind-3.8.1-proc-auxv.patch

# KDE#307828 - SSE optimized wcscpy, wcscmp, wcsrchr and wcschr trigger
# uninitialised value and/or invalid read warnings
Patch20:	valgrind-3.8.1-wcs.patch

# KDE#305728 - Add support for AVX2, BMI1, BMI2 and FMA instructions 
# Combined patch for:
# - valgrind-avx2-1.patch
# - valgrind-avx2-2.patch
# - valgrind-avx2-3.patch
# - valgrind-avx2-4.patch
# - valgrind-bmi-1.patch
# - valgrind-bmi-2.patch
# - valgrind-bmi-3.patch
# - valgrind-fma-1.patch
# - valgrind-memcheck-avx2-bmi-fma.patch
# - valgrind-vmaskmov-load.patch
# - valgrind-avx2-5.patch
# - valgrind-bmi-4.patch
# - valgrind-avx2-bmi-fma-tests.tar.bz2
#
# NOTE: Need to touch empty files from tar file:
# ./none/tests/amd64/avx2-1.stderr.exp
# ./none/tests/amd64/fma.stderr.exp
# ./none/tests/amd64/bmi.stderr.exp
Patch21:	valgrind-3.8.1-avx2-bmi-fma.patch.gz
# Small fixup for above patch, just a configure check.
# This is equivalent to valgrind-bmi-5.patch from KDE#305728
Patch22:	valgrind-3.8.1-bmi-conf-check.patch
# Partial backport of upstream revision 12884 without it AVX2 VPBROADCASTB
# insn is broken under memcheck.
Patch23:	valgrind-3.8.1-memcheck-mc_translate-Iop_8HLto16.patch
# vgtest files should prereq that the binary is there (for old binutils).
Patch24:	valgrind-3.8.1-avx2-prereq.patch

# KDE#308321 - testsuite memcheck filter interferes with gdb_filter
Patch25:	valgrind-3.8.1-filter_gdb.patch

# KDE#308341 - vgdb should report process exit (or fatal signal) 
Patch26:	valgrind-3.8.1-gdbserver_exit.patch

# KDE#164485 - VG_N_SEGNAMES and VG_N_SEGMENTS are (still) too small
Patch27:	valgrind-3.8.1-aspacemgr_VG_N_SEGs.patch

# KDE#308427 - s390 memcheck reports tsearch conditional jump or move
#              depends on uninitialized value [workaround, suppression]
Patch28:	valgrind-3.8.1-s390_tsearch_supp.patch

# KDE#307106 - unhandled instruction bytes: f0 0f c0 02 (lock xadd)
Patch29:	valgrind-3.8.1-xaddb.patch

# KDE#309427 - SSE optimized stpncpy trigger uninitialised value
Patch30:	valgrind-3.8.1-stpncpy.patch

# KDE#308573 - Internal Valgrind error on 64-bit instruction executed
#              in 32-bit mode
Patch31:	valgrind-3.8.1-ppc-32-mode-64-bit-instr.patch

# KDE#309425 - Provide a --sigill-diagnostics flag to suppress
#              illegal instruction reporting
Patch32:	valgrind-3.8.1-sigill_diag.patch

# Allow building against glibc-2.17. Upstream commit svn 13228.
Patch33:	valgrind-3.8.1-glibc-2.17.patch

# KDE#315441 - sendmsg syscall should ignore unset msghdr msg_flags
Patch34:	valgrind-3.8.1-sendmsg-flags.patch

# KDE#308886 - Missing support for PTRACE_SET/GETREGSET
Patch35:	valgrind-3.8.1-ptrace-setgetregset.patch

# KDE#310424 - --read-var-info does not properly describe static variables
Patch36:	valgrind-3.8.1-static-variables.patch

# KDE#316144, KDE#315959, KDE#316145 - various manpage fixes
Patch37:	valgrind-3.8.1-manpages.patch

# KDE#317091 Use -Wl,-Ttext-segment when static linking to keep build-ids
Patch38:	valgrind-3.8.1-text-segment.patch

# svn revisions 13348 and 13349
Patch39:	valgrind-3.8.1-regtest-fixlets.patch

# KDE#309600 - valgrind is a bit confused about 0-sized sections
Patch40:	valgrind-3.8.1-zero-size-sections.patch

# KDE#289360 - parse_type_DIE confused by DW_TAG_enumeration_type
Patch41:	valgrind-3.8.1-dwarf-anon-enum.patch

# KDE#321969 - Support [lf]setxattr on ppc32 and ppc64 linux kernel
Patch42:	valgrind-3.8.1-ppc-setxattr.patch

# KDE#321730 Add cg_merge and cg_diff man pages
# KDE#321738 Add manpages for vgdb and valgrind-listener
Patch43:	valgrind-3.8.1-new-manpages.patch

# KDE#320063 Support PTRACE_GET/SET_THREAD_AREA on x86.
Patch44:	valgrind-3.8.1-ptrace-thread-area.patch

# KDE#320116 Support Linux kernel AF_BLUETOOTH for bind()
Patch45:	valgrind-3.8.1-af-bluetooth.patch

URL: 		http://valgrind.org/
ExclusiveArch:	%{ix86} x86_64 ppc %arm
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
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
chmod 755 memcheck/tests/filter_memcpy
%patch18 -p1
%patch19 -p1
%patch20 -p1

# Add support for AVX2, BMI1, BMI2 and FMA instructions
%patch21 -p1
touch ./none/tests/amd64/avx2-1.stderr.exp
touch ./none/tests/amd64/fma.stderr.exp
touch ./none/tests/amd64/bmi.stderr.exp
%patch22 -p1
%patch23 -p1
%patch24 -p1

%patch25 -p1
%patch26 -p1
%patch27 -p1
%ifarch s390x
%patch28 -p1
%endif

%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
touch ./memcheck/tests/linux/getregset.stderr.exp
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1

# These tests go into an endless loop on ARM
# There is a __sync_add_and_fetch in the testcase.
# DRD is doing this trace printing inside the loop
# which causes the reservation (LDREX) to fail so
# it can never make progress.
%ifarch %{arm}
rm -f drd/tests/annotate_trace_memory_xml.vgtest
rm -f drd/tests/annotate_trace_memory.vgtest
%endif

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

