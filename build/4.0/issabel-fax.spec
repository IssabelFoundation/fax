%define modname fax

Summary: Issabel Fax Module
Name:    issabel-%{modname}
Version: 4.0.0
Release: 1
License: GPL
Group:   Applications/System
Source0: %{modname}_%{version}-%{release}.tgz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Requires(pre): issabel-framework >= 2.3.0-2
Requires(pre): iaxmodem, hylafax
# ghostscript supplies eps2eps, ps2pdfwr, gs
Requires: ghostscript
# tiff2pdf supplied by libtiff (CentOS), libtiff-tools (Fedora)
Requires: /usr/bin/tiff2pdf
Requires: php-PHPMailer

Obsoletes: elastix-fax

%description
Issabel Fax Module 

%prep
%setup -n %{name}_%{version}-%{release}

%install
rm -rf $RPM_BUILD_ROOT

# Files provided by all Issabel modules
mkdir -p    $RPM_BUILD_ROOT/var/www/html/
mv modules/ $RPM_BUILD_ROOT/var/www/html/

# Files personalities for hylafax
mkdir -p $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mkdir -p $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mkdir -p $RPM_BUILD_ROOT/var/spool/hylafax/etc/
mkdir -p $RPM_BUILD_ROOT/usr/share/issabel/privileged
mv setup/hylafax/bin/faxrcvd-issabel.php      $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mv setup/hylafax/bin/faxrcvd.php              $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mv setup/hylafax/bin/notify-issabel.php       $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mv setup/hylafax/bin/notify.php               $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mv setup/hylafax/bin/issabel-faxevent         $RPM_BUILD_ROOT/var/spool/hylafax/bin/
mv setup/hylafax/etc/FaxDictionary            $RPM_BUILD_ROOT/var/spool/hylafax/etc/
mv setup/hylafax/etc/config                   $RPM_BUILD_ROOT/var/spool/hylafax/etc/
mv setup/hylafax/etc/setup.cache              $RPM_BUILD_ROOT/var/spool/hylafax/etc/
mv setup/usr/share/issabel/privileged/*       $RPM_BUILD_ROOT/usr/share/issabel/privileged
rmdir setup/hylafax/bin setup/hylafax/etc/ setup/hylafax
rmdir setup/usr/share/issabel/privileged setup/usr/share/issabel setup/usr/share setup/usr

chmod    755 $RPM_BUILD_ROOT/var/spool/hylafax/bin/faxrcvd.php
chmod    755 $RPM_BUILD_ROOT/var/spool/hylafax/bin/faxrcvd-issabel.php
chmod    755 $RPM_BUILD_ROOT/var/spool/hylafax/bin/notify.php
chmod    755 $RPM_BUILD_ROOT/var/spool/hylafax/bin/notify-issabel.php

# move main library of FAX.
mkdir -p    $RPM_BUILD_ROOT/var/www/html/libs
mv setup/paloSantoFax.class.php               $RPM_BUILD_ROOT/var/www/html/libs/

# The following folder should contain all the data that is required by the installer,
# that cannot be handled by RPM.
mv setup/   $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mv menu.xml $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/

# new for fax
mkdir -p $RPM_BUILD_ROOT/var/log/iaxmodem
mkdir -p $RPM_BUILD_ROOT/var/spool/hylafax/bin
mkdir -p $RPM_BUILD_ROOT/var/spool/hylafax/etc
mkdir -p $RPM_BUILD_ROOT/var/www/faxes
mkdir -p $RPM_BUILD_ROOT/var/www/faxes/recvd
mkdir -p $RPM_BUILD_ROOT/var/www/faxes/sent

# ** Fax Visor additional config ** #
chmod 755 $RPM_BUILD_ROOT/var/www/faxes
chmod 775 $RPM_BUILD_ROOT/var/www/faxes/recvd $RPM_BUILD_ROOT/var/www/faxes/sent

%pre
mkdir -p /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
touch /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
if [ $1 -eq 2 ]; then
    rpm -q --queryformat='%{VERSION}-%{RELEASE}' %{name} > /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
fi

%post
# Habilito inicio automático de servicios necesarios
chkconfig --level 2345 hylafax on
chkconfig --level 2345 iaxmodem on

# Agrego Enlaces para Hylafax, ESTO AL PARECER LO HACE EL RPM DE HYLAFAX
ln -f -s pdf2fax.gs /var/spool/hylafax/bin/pdf2fax
ln -f -s ps2fax.gs  /var/spool/hylafax/bin/ps2fax

# Elimino archivos de fax que sobran
rm -f /etc/iaxmodem/iaxmodem-cfg.ttyIAX
rm -f /var/spool/hylafax/etc/config.ttyIAX

for i in `ls /var/spool/hylafax/etc/config.* 2>/dev/null`; do
  if [ "$i" != "/var/spool/hylafax/etc/config.sav" ]; then
    if [ "$i" != "/var/spool/hylafax/etc/config.devid" ]; then
      tilde=`echo $i | grep '~'`
      if [ "$?" -eq "1" ]; then
        if [ ! -L "$i" ]; then
          line="FaxRcvdCmd:              bin/faxrcvd.php"
          grep $line "$i" &>/dev/null
          res=$?
          if [ ! $res -eq 0 ]; then # no exists line
            echo "$line" >> $i
          fi
        fi
      fi
    fi
  fi
done

# Cambio de nombre de carpetas de faxes, esto es desde elastix 1.4
if [ -d "/var/www/html/faxes/recvq" ]; then
        mv /var/www/html/faxes/recvq/* /var/www/faxes/recvd
        rm -rf /var/www/html/faxes/recvq
fi

if [ -d "/var/www/html/faxes/sendq" ]; then
        mv /var/www/html/faxes/sendq/* /var/www/faxes/sent
        rm -rf /var/www/html/faxes/sendq
fi

if [ -d "/var/www/html/faxes" ]; then
        mv /var/www/html/faxes/* /var/www/faxes
fi

# Fix ownership and permission for sudo-less notification scripts
if [ $1 -eq 2 ]; then
	chmod 775 /var/www/faxes/recvd /var/www/faxes/sent
	chown asterisk.uucp /var/www/faxes/recvd /var/www/faxes/sent
fi

pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"
# Run installer script to fix up ACLs and add module to Elastix menus.
issabel-menumerge /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/menu.xml

pathSQLiteDB="/var/www/db"
mkdir -p $pathSQLiteDB
preversion=`cat $pathModule/preversion_%{modname}.info`
rm -f $pathModule/preversion_%{modname}.info

if [ $1 -eq 1 ]; then #install
  # The installer database
    issabel-dbprocess "install" "$pathModule/setup/db"
elif [ $1 -eq 2 ]; then #update
    issabel-dbprocess "update"  "$pathModule/setup/db" "$preversion"
fi

# The installer script expects to be in /tmp/new_module
mkdir -p /tmp/new_module/%{modname}
cp -r /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/* /tmp/new_module/%{modname}/
chown -R asterisk.asterisk /tmp/new_module/%{modname}

php /tmp/new_module/%{modname}/setup/installer.php


rm -rf /tmp/new_module

chmod 666 /var/www/db/fax.db

%clean
rm -rf $RPM_BUILD_ROOT

%preun
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"
if [ $1 -eq 0 ] ; then # Validation for desinstall this rpm
  echo "Delete Fax menus"
  issabel-menuremove "%{modname}"

  echo "Dump and delete %{name} databases"
  issabel-dbprocess "delete" "$pathModule/setup/db"
fi

%files
%defattr(-, root, root)
%{_localstatedir}/www/html/*
/usr/share/issabel/module_installer/*
/var/spool/hylafax/bin/*
/var/spool/hylafax/etc/setup.cache
%defattr(755, root, root)
/usr/share/issabel/privileged/*
%defattr(775, asterisk, uucp)
/var/www/faxes/recvd
/var/www/faxes/sent

%dir
/var/log/iaxmodem
%defattr(-, uucp, uucp)
%config(noreplace) /var/spool/hylafax/etc/FaxDictionary
%config(noreplace) /var/spool/hylafax/etc/config

%changelog
