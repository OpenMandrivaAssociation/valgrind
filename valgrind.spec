# WARNING: This package is synced with FC
%global _disable_lto %nil

%global __requires_exclude GLIBC_PRIVATE

#one of valgrind internal library is not linked to libc. Not sure if it should be fixed or not (since all test don't pass anyway), so disable check for now
%define _disable_ld_no_undefined 1

# disable debug package, it can prevent valgrind for working properly
#define debug_package   %{nil}

# (blino) FIXME: reenable qt4 as soon as availble in cauldron
%bcond_with	qt4

Summary:	Tool for finding memory management bugs in programs
Name:		valgrind
Version:	3.15.0
Release:	%mkrel 2
License:	GPLv2+
Group:		Development/Tools
URL:		http://valgrind.org/
ExclusiveArch: %{ix86} x86_64 ppc ppc64 ppc64le s390x %{arm} aarch64 %{riscv}
Obsoletes:	valgrind-plugins

# Note s390x doesn't have an openmpi port available.
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le %{arm} aarch64
%global build_openmpi 1
%else
%global build_openmpi 0
%endif

# Generating minisymtabs doesn't really work for the staticly linked
# tools. Note (below) that we don't strip the vgpreload libraries at all
# because valgrind might read and need the debuginfo in those (client)
# libraries for better error reporting and sometimes correctly unwinding.
# So those will already have their full symbol table.
%undefine _include_minidebuginfo

Source0: ftp://sourceware.org/pub/valgrind/valgrind-%{version}.tar.bz2

# From Fedora:

# Needs investigation and pushing upstream
Patch1: valgrind-3.9.0-cachegrind-improvements.patch

# KDE#211352 - helgrind races in helgrind's own mythread_wrapper
Patch2: valgrind-3.9.0-helgrind-race-supp.patch

# Make ld.so supressions slightly less specific.
Patch3: valgrind-3.9.0-ldso-supp.patch

# We want all executables and libraries in libexec instead of lib
# so they are only available for valgrind usage itself and so the
# same directory is used independent of arch.
Patch4: valgrind-3.15.0-pkglibexecdir.patch

# KDE#398649 s390x z13 support doesn't build with older gcc/binutils
# Disable z13 support (on rhel6)
Patch5: valgrind-3.15.0-disable-s390x-z13.patch

# Add some stack-protector
Patch6: valgrind-3.15.0-some-stack-protector.patch

# KDE#406561  mcinfcallWSRU gdbserver_test fails on ppc64
Patch7: valgrind-3.15.0-ppc64-filter_gdb.patch

# KDE#407218 Add support for the copy_file_range syscall
Patch8: valgrind-3.15.0-copy_file_range.patch

# KDE#407307 Intercept stpcpy also in ld.so for arm64
Patch9: valgrind-3.15.0-arm64-ld-stpcpy.patch

# commit 59784c aarch64 (arm64) isn't a supported architecture for exp-sgcheck.
Patch10: valgrind-3.15.0-exp-sgcheck-no-aarch64.patch

# commit 917e42 Make memcheck/tests/arm64-linux/scalar work under root
Patch11: valgrind-3.15.0-scalar-arm64.patch

# commit abc09f Make memcheck/tests/x86-linux/scalar test work under root.
Patch12: valgrind-3.15.0-scalar-x86.patch

# KDE#407764 s390x: drd fails on z13 due to function wrapping issue
Patch13: valgrind-3.15.0-s390x-wrap-drd.patch

# Add some -Wl,z,now.
Patch14: valgrind-3.15.0-some-Wl-z-now.patch

# KDE#408009 Expose rdrand and f16c even on avx if host cpu supports them
Patch15: valgrind-3.15.0-avx-rdrand-f16c.patch

# KDE#408091 Missing pkey syscalls
Patch16: valgrind-3.15.0-pkey.patch

#END OF FEDORA PATCHES
Patch1000: valgrind-3.13.0-arm.patch

BuildRequires:	glibc-static-devel
BuildRequires:	gdb
# (proyvind): build with support for OpenMP, boost & qt4 threads
BuildRequires:	libgomp-devel 
BuildRequires:	boost-devel
%if %{with qt4}
BuildRequires:	qt4-devel
%endif
Recommends:	gdb
%if %{build_openmpi}
BuildRequires: openmpi-devel >= 1.3.3
%endif
# Some testcases require g++ to build
BuildRequires: gcc-c++

# check_headers_and_includes uses Getopt::Long
BuildRequires: perl(Getopt::Long)

# We always autoreconf
BuildRequires: automake
BuildRequires: autoconf

# And only_arch, the configure option to only build for that arch.
%ifarch %{ix86}
%define only_arch --enable-only32bit
%endif
%ifarch %{x86_64}
%define only_arch --enable-only64bit
%endif
%ifarch %{arm}
%define only_arch --enable-only32bit
%endif
%ifarch aarch64
%define only_arch --enable-only64bit
%endif
%ifarch riscv64
%define only_arch --enable-only64bit
%endif

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

#--------------------------------------------------------------------

%package	devel
Summary:	Development files for valgrind
Group:		%{group}
Conflicts:	%{name} < 3.6.1-3

%description	devel
Header files and libraries for development of valgrind aware programs
or valgrind plugins.

%package tools-devel
Summary: Development files for building valgrind tools
Group: Development/Tools
Requires: valgrind-devel = %{version}-%{release}
Provides: %{name}-static = %{version}-%{release}

%description tools-devel
Header files and libraries for development of valgrind tools.
#--------------------------------------------------------------------

%if %{build_openmpi}
%package openmpi
Summary: OpenMPI support for valgrind
Group: Development/Tools
Requires: %{?scl_prefix}valgrind = %{version}-%{release}
Conflicts: valgrind <= 3.11.0-6.mga6

%description openmpi
A wrapper library for debugging OpenMPI parallel programs with valgrind.
See the section on Debugging MPI Parallel Programs with Valgrind in the
Valgrind User Manual for details.
%endif
#--------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# Old rhel gcc doesn't have -fstack-protector-strong.
%patch6 -p1

%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1

# This depends on patch6, old rhel gcc doesn't have -fstack-protector-strong.
%if 0%{?fedora} || 0%{?rhel} >= 7
%patch14 -p1
%endif

%patch15 -p1
%patch16 -p1

%patch1000 -p1

%build
export CC="%{_bindir}/gcc"
export CXX="%{_bindir}/g++"
autoreconf -fi
# Convert the library paths with /lib or /lib64 in the suppressions to those
# with /usr/lib or /usr/lib64 due to the /usrmove .
perl -pi -e 's!obj:/lib!obj:/usr/lib!g' *.supp *.supp.in

%define mpiccpath %{!?scl:%{_libdir}}%{?scl:%{_root_libdir}}/openmpi/bin/mpicc

# Filter out "hardening" flags that don't make sense for valgrind.
# -fstack-protector just cannot work (valgrind would have to implement
# its own version since it doesn't link with glibc and handles stack
# setup itself). We patch some flags back in just for those helper
# programs where it does make sense.
#
# -Wl,-z,now doesn't make sense for static linked tools
# and would prevent using the vgpreload libraries on binaries that
# don't link themselves against libraries (like pthread) which symbols
# are needed (but only if the inferior itself would use them).
#
# -O2 doesn't work for the vgpreload libraries either. They are meant
# to not be optimized to show precisely what happened. valgrind adds
# -O2 itself wherever suitable.
#
# On ppc64[be] -fexceptions is troublesome.
# It might cause an undefined reference to `_Unwind_Resume'
# in libcoregrind-ppc64be-linux.a(libcoregrind_ppc64be_linux_a-readelf.o):
# In function `read_elf_symtab__ppc64be_linux.
#
# Also disable strict symbol checks because the vg_preload library
# will use hidden/undefined symbols from glibc like __libc_freeres.

%ifarch ppc64
CFLAGS="`echo " %{optflags} " | sed 's/ -fstack-protector\([-a-z]*\) / / g;s/ -O2 / /g;s/ -fexceptions / /g;'`"
%else
CFLAGS="`echo " %{optflags} " | sed 's/ -fstack-protector\([-a-z]*\) / / g;s/ -O2 / /g;'`"
%endif
export CFLAGS

# Older Fedora/RHEL only had __global_ldflags.
# Even older didn't even have that (so we don't need to scrub them).
%if 0%{?build_ldflags:1}
LDFLAGS="`echo " %{build_ldflags} "    | sed 's/ -Wl,-z,now / / g;'`"
%else
%if 0%{?__global_ldflags:1}
LDFLAGS="`echo " %{__global_ldflags} " | sed 's/ -Wl,-z,now / / g;'`"
%endif
%endif
export LDFLAGS

%configure \
  %{only_arch} \
%if %{build_openmpi}
  --with-mpicc=%{mpiccpath} \
%endif
  GDB=%{_bindir}/gdb

%make_build

%install
# Don't strip (prevent valgrind from working properly, as explained in README_PACKAGERS)
export DONT_STRIP=1

# FIXME exporting DONT_STRIP=1 is causing some weird behavior with debug_package
# and causing it to not set DISABLE_DEBUG=1
#export DISABLE_DEBUG=1

%make_install


# We don't want debuginfo generated for the vgpreload libraries.
# Turn off execute bit so they aren't included in the debuginfo.list.
# We'll turn the execute bit on again in %%files.
chmod 644 $RPM_BUILD_ROOT%{_libexecdir}/valgrind/vgpreload*-*-*so

%check
# Make sure some info about the system is in the build.log
uname -a
rpm -q glibc gcc binutils || true
LD_SHOW_AUXV=1 /bin/true
cat /proc/cpuinfo

# Make sure a basic binary runs. There should be no errors.
./vg-in-place --error-exitcode=1 /bin/true --help

# Make sure no extra CFLAGS, CXXFLAGS or LDFLAGS leak through,
# the testsuite sets all flags necessary. See also configure above.
make %{?_smp_mflags} CFLAGS="" CXXFLAGS="" LDFLAGS="" check
# some tests are known to fail,
# just check no more tests are failing than Fedora ;)

echo ===============TESTING===================
# On arm the gdb integration tests hang for unknown reasons.
%ifarch %{arm}
  make nonexp-regtest || :
%else
  make regtest || :
%endif

# Make sure test failures show up in build.log
# Gather up the diffs (at most the first 20 lines for each one)
MAX_LINES=20
diff_files=`find gdbserver_tests */tests -name '*.diff*' | sort`
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

%files
%doc README* AUTHORS FAQ.txt NEWS docs/html
%exclude /usr/share/doc/valgrind/valgrind_manual.ps
%doc %{_docdir}/valgrind/valgrind_manual.pdf
%{_bindir}/*
%dir %{_libexecdir}/valgrind
# Install everything in the libdir except the .so.
# The vgpreload so files might need file mode adjustment.
%{_libexecdir}/valgrind/*[^o]
# Turn on executable bit again for vgpreload libraries.
# Was disabled in %%install to prevent debuginfo stripping.
%attr(0755,root,root) %{_libexecdir}/valgrind/vgpreload*-*-*so
%{_mandir}/man1/*

%files devel
%dir %{_includedir}/valgrind
%{_includedir}/valgrind/valgrind.h
%{_includedir}/valgrind/callgrind.h
%{_includedir}/valgrind/drd.h
%{_includedir}/valgrind/helgrind.h
%{_includedir}/valgrind/memcheck.h
%{_libdir}/pkgconfig/valgrind.pc

%files tools-devel
%{_includedir}/valgrind/config.h
%{_includedir}/valgrind/libvex*h
%{_includedir}/valgrind/pub_tool_*h
%{_includedir}/valgrind/vki
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.a

%if %{build_openmpi}
%files openmpi
%defattr(-,root,root)
%dir %{_libdir}/valgrind
#{_libdir}/openmpi/valgrind/libmpiwrap*.so
#{_libdir}/valgrind/libmpiwrap*.so
%endif


%changelog
* Mon Jul 01 2019 tv <tv> 3.15.0-2.mga8
+ Revision: 1416626
- sync patches with FC

* Mon Apr 22 2019 tv <tv> 3.15.0-1.mga7
+ Revision: 1394728
- valgrind-3.15.0 final
- Drop close_fds, it is no longer needed.

* Fri Apr 12 2019 tv <tv> 3.15.0-0.1.RC2.mga7
+ Revision: 1389357
- Update to 3.15.0.RC2.
- Drop upstreamed patches

* Wed Apr 10 2019 tv <tv> 3.15.0-0.1.RC1.mga7
+ Revision: 1387987
- Update to upstream 3.15.0-RC1

* Wed Mar 06 2019 tv <tv> 3.14.0-5.mga7
+ Revision: 1371822
- sync patches with FC
- sync patches with FC

* Wed Jan 16 2019 tv <tv> 3.14.0-4.mga7
+ Revision: 1357435
- sync patches with FC
- Update valgrind-3.14.0-jm-vmx-constraints.patch for ppc64.
- Show all diff files in check, not just the main/default one.

* Mon Dec 17 2018 tv <tv> 3.14.0-3.mga7
+ Revision: 1342254
- sync patches with FC

* Sun Dec 02 2018 tv <tv> 3.14.0-2.mga7
+ Revision: 1337374
- sync patches with FC

* Sat Oct 13 2018 tv <tv> 3.14.0-1.mga7
+ Revision: 1319936
- 3.14.0 final

* Thu Oct 04 2018 tv <tv> 3.14.0-0.1RC2.mga7
+ Revision: 1317553
- Upgrade to RC2

* Thu Sep 20 2018 tv <tv> 3.14.0-0.1GIT.mga7
+ Revision: 1279588
- New upstream (pre-)release (mga#23397)
- Add valgrind-3.14.0-add-vector-h.patch

* Fri Sep 14 2018 tv <tv> 3.13.0-16.mga7
+ Revision: 1258947
- utimensat should ignore tv_sec for UTIME_NOW or UTIME_OMIT (KDE#397354)

* Fri Aug 10 2018 tv <tv> 3.13.0-15.mga7
+ Revision: 1250938
- sync patches with RH

* Wed Jun 20 2018 tv <tv> 3.13.0-14.mga7
+ Revision: 1238319
- Improved valgrind-3.13.0-arm64-hwcap.patch
- Add valgrind-3.13.0-arm64-ptrace.patch

* Wed May 09 2018 tv <tv> 3.13.0-13.mga7
+ Revision: 1227857
- Add valgrind-3.13.0-build-id-phdrs.patch (rhbz#1566639)
- Add valgrind-3.13.0-ppc64-mtfprwa-constraint.patch.

* Mon Mar 12 2018 tv <tv> 3.13.0-12.mga7
+ Revision: 1208615
- Split valgrind-tools-devel from valgrind-devel.
  (thus fixing gnome-build's build)
- use newer macros

* Sun Jan 07 2018 tv <tv> 3.13.0-10.mga7
+ Revision: 1191352
- sync patches with FC

* Sat Dec 30 2017 cjw <cjw> 3.13.0-9.mga7
+ Revision: 1187930
- fix build for arm
- add patch19 from fedora

* Tue Dec 12 2017 tv <tv> 3.13.0-8.mga7
+ Revision: 1182434
- Fix gnu debug alt file resolving

* Wed Oct 18 2017 tv <tv> 3.13.0-7.mga7
+ Revision: 1172612
- new release
- fix source URL
- sync patches with RH
- fix handling command line option --xml-socket

* Thu Jul 20 2017 tv <tv> 3.12.0-6.mga7
+ Revision: 1125666
- sync patches with FC

* Sat Jun 24 2017 luigiwalser <luigiwalser> 3.12.0-5.mga6
+ Revision: 1108344
- add patch from ubuntu to fix CVE-2016-4491 (mga#21126)

* Tue Dec 06 2016 tv <tv> 3.12.0-4.mga6
+ Revision: 1072737
- fix testsuite (rhbz#1390282)
- replace most of armv5 patch by a simple sed command

* Tue Oct 25 2016 tv <tv> 3.12.0-3.mga6
+ Revision: 1063479
- rediff armv5 "patch"

* Tue Oct 25 2016 tv <tv> 3.12.0-2.mga6
+ Revision: 1063469
- patch 1000: try to fix linking on arm

* Tue Oct 25 2016 tv <tv> 3.12.0-1.mga6
+ Revision: 1063449
- final release

* Fri Oct 21 2016 tv <tv> 3.12.0-0.1.RC2.mga6
+ Revision: 1062884
- 3.12.0.RC2

* Thu Jul 28 2016 tv <tv> 3.11.0-14.mga6
+ Revision: 1043819
- fix devel pkg summary
- sync patches with FC
- apply patches like FC does

* Thu Jun 30 2016 tv <tv> 3.11.0-13.mga6
+ Revision: 1038188
- sync patches with FC

* Mon May 09 2016 tv <tv> 3.11.0-12.mga6
+ Revision: 1011787
- sync patches with FC
- sync patches with FC

* Fri Apr 22 2016 tv <tv> 3.11.0-11.mga6
+ Revision: 1004923
- sync patches with FC

* Wed Apr 13 2016 tv <tv> 3.11.0-10.mga6
+ Revision: 1001076
- sync patches with FC
- switch to %%autopatch

* Sun Mar 06 2016 tv <tv> 3.11.0-9.mga6
+ Revision: 986854
- further adjust file list
- try to fix openmpi support
- further adjust file list (openmpi support seems broken?)
- adjust file list
- fix chmod
- move a lib in openmpi subpackage
- move a lib in openmpi subpackage
- move a lib in openmpi subpackage
- move *.a in devel package
- sync patches with RH

* Thu Jan 21 2016 tv <tv> 3.11.0-6.mga6
+ Revision: 926191
- sync patches with RH

* Sun Jan 17 2016 tv <tv> 3.11.0-5.mga6
+ Revision: 924821
- sync patches with FC
- notice that this package is synced with FC
+ pterjan <pterjan>
- Fix arm patch

* Sun Nov 29 2015 tv <tv> 3.11.0-4.mga6
+ Revision: 907211
- sync patches with FC

* Sun Nov 22 2015 pterjan <pterjan> 3.11.0-3.mga6
+ Revision: 904917
- Make it build on armv5tl

* Wed Sep 30 2015 tv <tv> 3.11.0-2.mga6
+ Revision: 885246
- rebuild for new libmpi

* Thu Sep 24 2015 tv <tv> 3.11.0-1.mga6
+ Revision: 883298
- fix doc packaging
- try to fix debuginfo
- new release

* Fri Jul 24 2015 tv <tv> 3.10.1-4.mga6
+ Revision: 857020
- sync patches with FC

* Sun Jun 28 2015 tv <tv> 3.10.1-3.mga6
+ Revision: 846670
- fix mismerge
- sync patches with FC (kernel-4+ support)

* Fri Feb 20 2015 tv <tv> 3.10.1-2.mga5
+ Revision: 816078
- sync patches with FC

* Sat Jan 24 2015 tv <tv> 3.10.1-1.mga5
+ Revision: 812110
- new version
- sync patches with FC

* Wed Oct 22 2014 tv <tv> 3.10.0-3.mga5
+ Revision: 792474
- sync patches with FC

* Wed Oct 15 2014 umeabot <umeabot> 3.10.0-2.mga5
+ Revision: 743654
- Second Mageia 5 Mass Rebuild
+ tv <tv>
- use %%global for req/prov exclude
- autoconvert to new prov/req excludes
- s/uggests:/Recommends:/

* Fri Sep 12 2014 tv <tv> 3.10.0-1.mga5
+ Revision: 674779
- 3.10.0 final

* Wed Sep 10 2014 tv <tv> 3.10.0-0.2.BETA2.mga5
+ Revision: 674502
- handle glibc-2.20

* Tue Sep 09 2014 tv <tv> 3.10.0-0.1.BETA2.mga5
+ Revision: 674079
- 3.10.0 BETA2
- don't run dwz or generate minisymtab
  (instead of disabling the whole debuginfo package)

* Wed Sep 03 2014 tv <tv> 3.10.0-0.1.BETA1.mga5
+ Revision: 671350
- 3.10.0 BETA1
- enables inlined frames in stacktraces

* Mon Sep 01 2014 luigiwalser <luigiwalser> 3.9.0-9.svn20140829r14384.mga5
+ Revision: 670358
- remove epoch from requires for valgrind-openmpi

* Sun Aug 31 2014 tv <tv> 3.9.0-8.svn20140829r14384.mga5
+ Revision: 669841
- fix group
- enable openmpi support

* Fri Aug 29 2014 tv <tv> 3.9.0-7.svn20140829r14384.mga5
+ Revision: 669299
- update to upstream svn r14384

* Wed Aug 27 2014 tv <tv> 3.9.0-7.svn20140827r14371.mga5
+ Revision: 668833
- update to upstream svn r14370

* Wed Aug 27 2014 tv <tv> 3.9.0-7.svn20140809r14250.mga5
+ Revision: 668592
- fix default suppresions file location

* Tue Aug 12 2014 tv <tv> 3.9.0-6.svn20140809r14250.mga5
+ Revision: 661862
- new release

* Sat Aug 02 2014 tv <tv> 3.9.0-6.svn20140718r14176.mga5
+ Revision: 659299
- new snapshot
- sync patches with RH

* Fri Feb 28 2014 tv <tv> 3.9.0-6.mga5
+ Revision: 597955
- sync patches with RH:
  o Add upstream fixes to valgrind-3.9.0-timer_create.patch
  o Add valgrind-3.9.0-glibc-2.19.patch
  o Add valgrind-3.9.0-s390-dup3.patch
  o Add valgrind-3.9.0-timer_create.patch

* Mon Feb 17 2014 tmb <tmb> 3.9.0-5.mga5
+ Revision: 593950
- rebuild with new glibc

* Sun Feb 09 2014 pterjan <pterjan> 3.9.0-3.mga5
+ Revision: 587806
- Fix spec
+ tv <tv>
- sync patches with RH

* Sun Feb 09 2014 tmb <tmb> 3.9.0-2.mga5
+ Revision: 587781
- support glibc 2.19 (P7, Arch)
- rebuild for new glibc

* Tue Nov 05 2013 tv <tv> 3.9.0-1.mga4
+ Revision: 549603
- new release 3.9.0
- package NEWS
- kill patches that are now upstream
- sync patches with FC

* Mon Oct 21 2013 umeabot <umeabot> 3.8.1-14.mga4
+ Revision: 539058
- Mageia 4 Mass Rebuild

* Fri Oct 04 2013 tv <tv> 3.8.1-13.mga4
+ Revision: 491272
- sync with FC:
  o rename patch 50 a 52
  o filter out -mcpu= so tests are compiled with the right flags (rhbz#996927)
  o implement SSE4 MOVNTDQA insn
  o fix power_ISA2_05 testcase
  o fix ppc32 make check build
  o add valgrind-3.8.1-mmxext.patch

* Fri Oct 04 2013 shlomif <shlomif> 3.8.1-12.mga4
+ Revision: 491263
- Get rid of trailing whitespace in the spec
- Fix for RH#1011713. Broke some tests.

* Wed Aug 21 2013 tv <tv> 3.8.1-11.mga4
+ Revision: 469105
- Allow building against glibc 2.18 (rhbz#999169)

* Wed Aug 21 2013 tv <tv> 3.8.1-10.mga4
+ Revision: 468611
- sync patches with FC

* Mon Jul 15 2013 tv <tv> 3.8.1-9.mga4
+ Revision: 454891
- sync patches with RH

* Mon Jul 08 2013 fwang <fwang> 3.8.1-8.mga4
+ Revision: 451225
- rebuild for new boost
+ tv <tv>
- sync patches with FC

* Mon May 27 2013 tv <tv> 3.8.1-7.mga4
+ Revision: 428964
- sync patches with FC

* Mon Jan 14 2013 umeabot <umeabot> 3.8.1-6.mga3
+ Revision: 385224
- Mass Rebuild - https://wiki.mageia.org/en/Feature:Mageia3MassRebuild

* Sun Jan 06 2013 cjw <cjw> 3.8.1-5.mga3
+ Revision: 339934
- patch103: allow to build with glibc 2.17

* Fri Dec 14 2012 tv <tv> 3.8.1-4.mga3
+ Revision: 330586
- rebuild for new gdb

* Sun Nov 18 2012 tv <tv> 3.8.1-3.mga3
+ Revision: 319493
- sync patches with FC (after fixing them trying to patch .orig files...)
+ malo <malo>
- update RPM group

* Thu Oct 11 2012 tv <tv> 3.8.1-2.mga3
+ Revision: 304680
- sync patches with FC

* Wed Sep 26 2012 tv <tv> 3.8.1-1.mga3
+ Revision: 297921
- new release
- sync with FC patches

* Mon Aug 27 2012 tv <tv> 3.8.0-4.mga3
+ Revision: 284624
- new release

* Tue Aug 21 2012 tv <tv> 3.8.0-3.mga3
+ Revision: 282942
- patch 100: fix a crash with mini debug info

* Mon Aug 20 2012 blino <blino> 3.8.0-2.mga3
+ Revision: 282510
- add valgrind-3.8.0-find-buildid.patch workaround from Fedora (RH#849435 KDE#305431)

* Mon Aug 13 2012 tv <tv> 3.8.0-1.mga3
+ Revision: 281166
- drop patch  (what comment said was merged)
- drop merged glibc-2.16 patch
- drop now useless automake patch
- drop merged FC patches
- add new patches from FC
- add one patch from FC (on i?86 prefer to use CFI over %%ebp unwinding, as GCC
  4.6+ defaults to -fomit-frame-pointer)
- like FC, filter out some compilation flags (getting rid of new cloberring
  issues due to -fPIC on x86_64)
- fix install

* Sat Aug 11 2012 blino <blino> 3.7.0-5.mga3
+ Revision: 280480
- add patches from Fedora (and upstream valgrind) to handle dwz DWARF compressor output

* Wed Jul 25 2012 shlomif <shlomif> 3.7.0-4.mga3
+ Revision: 274227
- Convert paths to /usr/lib* instead of /lib* in the suppressions.
  This is another fallout of the /usr-move.

* Sat Jul 21 2012 shlomif <shlomif> 3.7.0-3.mga3
+ Revision: 273153
- Add a blurb to the patch
- New release for glibc-2.16.x.
  1. Fix build with new automake.
  2. Update the valgrind package to accept building against 2.16 (with a patch
  derived from the svn).
  3. Fix problems with unpacked files.
  4. Put a symlink to a place that valgrind is looking for.

* Wed Dec 21 2011 shlomif <shlomif> 3.7.0-1.mga2
+ Revision: 185524
- Cancel make regtest because it hangs.
+ fwang <fwang>
- sync with mandriva package

* Thu Oct 27 2011 shlomif <shlomif> 3.6.1-5.mga2
+ Revision: 158760
- Applied patches to build against kernel-3.x and glibc-2.14.x

* Wed Jun 22 2011 ahmad <ahmad> 3.6.1-4.mga2
+ Revision: 111971
- Add conflicts to ease updates after the -devel split (from tv)
- Re-enable building with qt4
- Only run autoreconf when building with qt4
- Drop unapplied patch3

* Tue Jun 07 2011 dmorgan <dmorgan> 3.6.1-3.mga2
+ Revision: 101519
- Provide devel subpackage  ( partial merge of mdv commit 659516)

* Sun May 15 2011 pterjan <pterjan> 3.6.1-2.mga1
+ Revision: 99037
- Rebuild for fixed find-requires

* Sat Apr 16 2011 pterjan <pterjan> 3.6.1-1.mga1
+ Revision: 86603
- Update to 3.6.1

* Tue Jan 11 2011 blino <blino> 3.6.0-2.mga1
+ Revision: 6503
- do not build with qt4 support for now
- remove versions in comments
- imported package valgrind

