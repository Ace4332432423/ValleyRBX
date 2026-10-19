# 🌌 ValleyRBX

**ValleyRBX** is a cinematic, luxury Linux environment manager and bootstrapper for **Roblox Studio**, engineered specifically for **CachyOS / Arch Linux** with **Vinegar's patched Kombucha Wine runner**.

Featuring deep cosmic obsidian and aurora violet gradients, fluid easing animations, and dual desktop integration.

---

## 📸 Visuals & Cinematic Experience

- **Obsidian & Aurora Violet Aesthetic:**
  - Glassmorphic translucent cards with glowing border gradients (`rgba(168, 85, 247, 0.45)`).
  - Luminous multi-stop gradient launch buttons and status badges.
- **Fluid Micro-Animations:**
  - Smooth easing curves on toggle switches (`QEasingCurve.Type.InOutCubic`).
  - Cross-fade opacity transitions between configuration panels (`QGraphicsOpacityEffect`).
- **Cinematic Frameless Direct-Launch Splash:**
  - Displays your custom rounded icon with an animated progress bar and stage status during direct launch.

---

## 🚀 Dual Desktop Integration

ValleyRBX provides two desktop shortcuts ready to launch from your CachyOS application menu:

1. **⚡ ValleyRBX** (`ValleyRBX.desktop`):
   - **Direct Launch Mode:** Instantly launches Roblox Studio with your saved FastFlags, Wine prefix, custom environment variables, and CEF mitigations. Shows the cinematic splash banner while Wine initializes.
2. **🍷 ValleyRBX Manage** (`ValleyRBX-manage.desktop`):
   - **Management Mode:** Opens the full ValleyRBX control center where you can edit Wine prefixes (`winecfg`), change renderers (DXVK, Vulkan, OpenGL), add environment variables, toggle CEF web pages, and customize FastFlags.

---

## 🛠️ Feature Matrix

- **🍷 Wine & Prefix Manager:**
  - Switch between or create 64-bit Wine prefixes.
  - Buttons for **`winecfg`**, **`regedit`**, **`winetricks`**, and direct **`drive_c` browsing**.
  - Instant btrfs copy-on-write prefix cloning (`cp -a --reflink=auto`).
  - Kill stuck `wineserver` processes with one click.
  - Sits directly on top of Vinegar's **Kombucha Wine** runner with patched CEF child-window support.

- **🎨 Graphics Renderer & Environment Variables:**
  - Switch graphics backends: **Direct3D 11 (DXVK)**, **Vulkan (Native)**, **OpenGL**, and **Direct3D 12 (VKD3D)**.
  - Interactive table to add and delete custom environment variables.
  - Pre-configured toggles for `WINEFSYNC` (`futex_waitv`), `DXVK_ASYNC`, and Wayland Gamescope isolation.

- **🌐 Web Pages / CEF Control:**
  - **Disable Web Pages (Recommended):** Eliminates 90% of Wine Studio white-screen lockups and GPU-process crashes by injecting `FFlagStudioDisableCEF`.
  - **Software Rendered CEF:** Disables GPU acceleration for CEF (`--disable-gpu`) while keeping the Start Page & Toolbox accessible.
  - **Standard CEF:** Hardware-accelerated embedded browser using Kombucha's window patches.
  - **External Browser Redirect:** Directs asset links to your Linux browser via `xdg-open`.

- **⚡ FastFlags Menu & Presets:**
  - Allowlisted flags table (CSG LOD distance, grass distance, manual texture quality, DPI scaling disable, and MSAA anti-aliasing).
  - Presets: **Performance**, **High Quality**, and **Stability**.
  - Add custom flags with automatic type detection (`bool`, `int`, `string`).
  - Dual sync to both Vinegar's overlay (`~/.config/vinegar/overlay/studio/ClientSettings/`) and installed Studio versions.

- **📜 Live Logs & CachyOS Platform Audit:**
  - Real-time colorized stdout/stderr console.
  - Hardware audit for Arch `[multilib]`, 32-bit graphics runtimes, BORE/sched-ext schedulers, and NVIDIA RTX 3060 driver status.

---

## 📦 Installation (Arch / CachyOS)

```bash
# Clone the repository
git clone https://github.com/yourusername/ValleyRBX.git
cd ValleyRBX

# Build and install the package (requires base-devel)
makepkg -si
```

The PKGBUILD will install the `valleyrbx` command, desktop entries, and required resources.

## ▶️ Running

- **Launch Studio**: `valleyrbx --launch`
- **Open Manager**: `valleyrbx --manage`

