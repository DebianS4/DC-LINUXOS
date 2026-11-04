#!/bin/sh
set -eu
cd "$(dirname "$0")"
sudo lb clean --purge
if [ -d .build ]; then
  sudo chown -R "$(id -u):$(id -g)" .build
fi
lb config --mode debian --distribution trixie --architectures amd64 \
  --binary-images iso-hybrid \
  --archive-areas 'main contrib non-free non-free-firmware' \
  --debian-installer live \
  --bootappend-live 'boot=live components quiet splash username=nucleo hostname=nucleo' \
  --iso-application 'Nucleo Linux Live' \
  --iso-publisher 'Nucleo Linux Project' \
  --iso-volume 'NUCLEO_1_0' \
  --checksums sha256 --compression xz \
  --firmware-binary true --firmware-chroot true \
  --apt-recommends true \
  --linux-packages linux-image --linux-flavours amd64 \
  --system live --initramfs live-boot --initsystem systemd \
  --binary-filesystem fat32 --memtest none --source false \
  --win32-loader false
sudo env DEBIAN_FRONTEND=noninteractive lb build
