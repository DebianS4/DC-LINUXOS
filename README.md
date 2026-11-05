<div align="center">
  <img src="assets/dc-linuxos-logo.png" alt="Logo de DC-LINUX OS" width="190">
  <h1>DC-LINUX OS · Núcleo Linux 1.0</h1>
  <p>Edición Live basada en Debian 13 (Trixie), con escritorio XFCE.</p>
  <p>
    <a href="https://debians4.github.io/DC-LINUXOS/">Sitio web</a> ·
    <a href="https://github.com/DebianS4/DC-LINUXOS">Repositorio</a> ·
    <a href="https://gooey.ai/2/keyRb">El Laboratorio</a> ·
    <a href="SECURITY.md">Política de seguridad</a>
  </p>
  <p>
    <a href="https://github.com/DebianS4/DC-LINUXOS/releases/tag/nucleo-2026-11-04"><img src="https://img.shields.io/badge/Release-N%C3%BAcleo%20Linux%201.0-0A66C2?style=for-the-badge&logo=github&logoColor=white" alt="Release Núcleo Linux 1.0"></a>
    <img src="https://img.shields.io/badge/Arquitectura-amd64-2563EB?style=for-the-badge" alt="Arquitectura amd64">
    <img src="https://img.shields.io/badge/Escritorio-XFCE-168DE2?style=for-the-badge&logo=xfce&logoColor=white" alt="Escritorio XFCE">
    <a href="https://github.com/DebianS4/DC-LINUXOS/actions/workflows/site-checks.yml"><img src="https://github.com/DebianS4/DC-LINUXOS/actions/workflows/site-checks.yml/badge.svg?branch=main" alt="Estado del build del sitio"></a>
  </p>
  <p>
    <a href="https://github.com/DebianS4/DC-LINUXOS"><img src="https://img.shields.io/github/stars/DebianS4/DC-LINUXOS?style=social" alt="Estrellas en GitHub"></a>
  </p>
</div>

![Vista previa del escritorio de Núcleo Linux con XFCE](assets/nucleo-desktop-preview.png)

## DC-LINUX para PC

Núcleo Linux es una imagen Live híbrida para equipos **amd64 (x86_64)**, con arranque **BIOS y UEFI**. Incluye XFCE, Firefox ESR, NetworkManager, firmware y herramientas básicas del escritorio. El tema usa el fondo de Núcleo y el cursor **DC-Red-Luminous**.

[**Release y descargas de Núcleo Linux 1.0**](https://github.com/DebianS4/DC-LINUXOS/releases/tag/nucleo-2026-11-04)

La ISO se distribuye en dos partes. Descarga `.part00`, `.part01` y el archivo `.sha256` en una misma carpeta.

En Linux/WSL, reconstruye y verifica la ISO:

```sh
cat live-image-amd64.hybrid.iso.part00 live-image-amd64.hybrid.iso.part01 > live-image-amd64.hybrid.iso
sha256sum -c live-image-amd64.hybrid.iso.sha256
```

En macOS, usa `shasum -a 256 -c live-image-amd64.hybrid.iso.sha256` para comprobar el checksum. En Windows, desde Símbolo del sistema:

```bat
copy /b live-image-amd64.hybrid.iso.part00+live-image-amd64.hybrid.iso.part01 live-image-amd64.hybrid.iso
```

SHA-256 esperado para la ISO reconstruida:

```text
94e3e87f82210501c812ad7a3b062ff6620eee5e56c07cdf192542463b9d9e47
```

## Compilar

Compila en Debian o Ubuntu con al menos **25 GB libres**. Se requieren `live-build` `1:20250505+deb13u1` o posterior, `debootstrap`, `xorriso`, `squashfs-tools`, `dosfstools`, `mtools`, `grub-pc-bin` y `grub-efi-amd64-bin`. El script utiliza `sudo`.

Desde la raíz del repositorio:

```sh
./build.sh
```

El proceso limpia artefactos previos, configura `live-build` y genera la ISO, el manifiesto de paquetes y las sumas SHA-256. La primera compilación descarga paquetes de Debian.

## Raspberry Pi

Las imágenes y sus checksums están enlazados en la [página unificada de descargas](https://debians4.github.io/DC-LINUXOS/#raspberry-pi).

- **Zero W 1.1:** Edición especial para Raspberry Pi Zero W 1.1. Imagen ARMv6 de 32 bits, disponible en el [release de imágenes mínimas](https://github.com/DebianS4/DC-LINUXOS/releases/tag/rpi-minimal-2026.11.04).
- **Pi 4 / Pi 5:** imagen mínima ARM64 de 64 bits, en el mismo [release](https://github.com/DebianS4/DC-LINUXOS/releases/tag/rpi-minimal-2026.11.04).
- **Pi 4 · escritorio:** imagen ARM64 disponible en el [release de escritorio](https://github.com/DebianS4/DC-LINUXOS/releases/tag/rpi4-desktop-2026.11.04).

Los checksums permiten comparar cada archivo con el valor publicado; no sustituyen una firma digital ni prueban por sí solos la autoría del archivo.
