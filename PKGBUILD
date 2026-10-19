# Maintainer: Antigravity Team
pkgname=valleyrbx
pkgver=1.0.0
pkgrel=1
pkgdesc="Cinematic Linux Roblox Studio Runtime with Vinegar Kombucha Wine Handler"
arch=('any')
url="https://github.com/vinegarhq/vinegar"
license=('GPL-3.0-or-later')
depends=(
    'python>=3.11'
    'pyside6'
    'vinegar'
)
optdepends=(
    'gamescope: Fixes Wayland mouse capture and cursor locking'
    'mangohud: In-game FPS & performance overlay'
    'winetricks: Prefix library management tool'
)
source=()

package() {
    cd "$srcdir/.."
    mkdir -p "$pkgdir/usr/lib/$pkgname"
    cp -r src/studio_strapper "$pkgdir/usr/lib/$pkgname/"

    mkdir -p "$pkgdir/usr/bin"
    cat << 'EOF' > "$pkgdir/usr/bin/valleyrbx"
#!/usr/bin/env bash
export PYTHONPATH="/usr/lib/valleyrbx:$PYTHONPATH"
exec python3 -m studio_strapper "$@"
EOF
    chmod +x "$pkgdir/usr/bin/valleyrbx"

    mkdir -p "$pkgdir/usr/share/applications"
    install -Dm644 ValleyRBX.desktop "$pkgdir/usr/share/applications/ValleyRBX.desktop"
    install -Dm644 ValleyRBX-manage.desktop "$pkgdir/usr/share/applications/ValleyRBX-manage.desktop"
}
