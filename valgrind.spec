%define	name	valgrind
%define	version	3.2.3
%define	release	%mkrel 1
%define _requires_exceptions GLIBC_PRIVATE

Name: 		%{name}
Version:	%{version}
Release:	%{release}
Summary: 	an open-source memory debugger for x86-linux
License: 	GPL
Group: 		Development/Other
Source0:	http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
Source1: 	valgrind
URL: 		http://valgrind.kde.org/
ExclusiveArch:	%{ix86} x86_64 ppc
BuildRequires:	glibc-static-devel
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

%build
%configure2_5x
%make



%install
rm -rf %{buildroot}
# Don't strip librairy ask by developer
export DONT_STRIP=1
%makeinstall
# move documentation where rpm expect it to be
mv %{buildroot}%{_datadir}/doc/%{name} %{buildroot}%{_datadir}/doc/%{name}-%{version}
install -m 644 README* ACKNOWLEDGEMENTS  %{buildroot}%{_datadir}/doc/%{name}-%{version}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{_libdir}/%name
%{_includedir}/valgrind/
%{_libdir}/pkgconfig/valgrind.pc
%{_datadir}/doc/%{name}-%{version}
%{_mandir}/man1/valgrind.1.bz2


