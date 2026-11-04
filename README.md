# Núcleo Linux 1.0

Edición Live ligera basada en Debian 13 (Trixie), amd64 y XFCE. La imagen admite arranque BIOS y UEFI; incluye firmware amplio, NetworkManager, Firefox ESR y la opción de instalador Live de Debian.

## Requisitos de compilación

Compilar en Debian o Ubuntu con conexión a Internet y al menos 25 GB libres. Se requiere `live-build` 1:20250505+deb13u1 o posterior, `debootstrap`, `xorriso`, `squashfs-tools`, `dosfstools`, `mtools`, `grub-pc-bin`, `grub-efi-amd64-bin` y llavero de Debian que incluya las claves de Trixie. La compilación necesita `sudo`.

## Construir

Desde la raíz del repositorio, ejecutar:

```sh
./build.sh
```

El script limpia los artefactos anteriores, restaura la configuración, y genera el ISO híbrido, el manifiesto y las sumas SHA-256 en el directorio raíz del proyecto. El primer build descarga paquetes de Debian y puede tardar bastante según la red.

## Contenido ligero

Se usa XFCE en lugar de un escritorio GNOME/KDE completo. Incluye navegador, terminal, editor de texto, visor de imágenes, gestión de red y firmware; evita suites ofimáticas y aplicaciones duplicadas para contener el tamaño.

## Escritorio predeterminado

La sesión XFCE incluye el fondo de Núcleo, un cursor rojo brillante `DC-Red-Luminous`, reloj en el panel superior y una barra de aplicaciones centrada en la parte inferior.

## Descargar la ISO

La [última publicación](https://github.com/DebianS4/DC-LINUXOS/releases/latest) distribuye la ISO en dos partes para respetar el límite de tamaño por archivo de GitHub Releases. Descarga ambas partes y el archivo SHA-256; en Linux o macOS, reconstruye y verifica la imagen así:

```sh
cat live-image-amd64.hybrid.iso.part00 live-image-amd64.hybrid.iso.part01 > live-image-amd64.hybrid.iso
sha256sum -c live-image-amd64.hybrid.iso.sha256
```

En Windows, puedes reconstruirla desde Símbolo del sistema con `copy /b live-image-amd64.hybrid.iso.part00+live-image-amd64.hybrid.iso.part01 live-image-amd64.hybrid.iso`.

## Sitio web de DC-LINUX

La landing visual del proyecto está en [`website/`](website/). Usa una identidad azul y negra inspirada en el escritorio Núcleo XFCE, con secciones sobre el sistema, características, galería y enlaces a las releases y al código fuente.

Para verla localmente:

```sh
cd website
npm start
```

Después abre `http://localhost:3000`.

## Alcance de verificación

La compilación en CI o contenedores puede fallar si el entorno prohíbe montajes, namespaces o `chroot`. Antes de distribuir la imagen, arrancarla en una máquina virtual y comprobar red, Wi-Fi, audio, gráficos e instalación en hardware real.
