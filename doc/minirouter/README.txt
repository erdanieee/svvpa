- Seguir instrucciones de instalación de https://wiki.openwrt.org/toh/unbranded/a5-v11
    * actualizar firmware de fábrica con versión factory de openwrt

- compilar versión openwrt con imagebuilder:
    * make image PROFILE=A5-V11 PACKAGES="comgt kmod-usb-serial kmod-usb-serial-option kmod-usb-serial-wwan usb-modeswitch picocom busybox chat dnsmasq firewall iw opkg swconfig smstools3"
    
- subir versión sysupgrade usando la web

- entrar con telnet y poner clave root para poder entrar a partir de ese momento con ssh

- copiar los ficheros de configuración a /etc/config /etc/init.d y /root/bin

- dar permiso de ejecución a /etc/config/init.d/modem3g e iniciar automáticamente on boot
    * /etc/init.d/modem3g enable

- dar permisos de ejecución a /etc/bin/*
 
- Meter en /etc/rc.local
swconfig dev switch0 port 1 set disable 1
swconfig dev switch0 port 2 set disable 1
swconfig dev switch0 port 3 set disable 1
swconfig dev switch0 port 4 set disable 1
swconfig dev switch0 set apply

- poner ssh desde svvpa sin password



