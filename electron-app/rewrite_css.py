import codecs

css_path = 'src/renderer/src/style.css'
with codecs.open(css_path, 'r', 'utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
test_idx = len(lines)

for i, line in enumerate(lines):
    if '.theme-luxury .liquid-player {' in line and start_idx == -1:
        start_idx = i
    elif '.player-shell.theme-radio {' in line:
        end_idx = i
    elif '/* TEST UI FOR SOURCE PANEL */' in line:
        test_idx = i
        break

new_css = """
/* Liquid Glass control theme: pure dark mode UI with glass cards. */
.control-shell.theme-luxury {
  position: relative;
  isolation: isolate;
  display: block;
  width: 100vw;
  height: 100vh;
  padding: 26px;
  overflow-y: auto;
  color: #f8fafc;
  background:
    radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.13), transparent 34%),
    radial-gradient(circle at 82% 76%, rgba(139, 92, 246, 0.16), transparent 36%),
    linear-gradient(135deg, #071126 0%, #02040b 50%, #09152a 100%);
  background-attachment: fixed;
  font-family:
    "SF Pro Display",
    "Segoe UI Variable Display",
    "Microsoft JhengHei UI",
    system-ui,
    sans-serif;
}

/* Glass Card styles mapped to control panels and widgets */
.control-shell.theme-luxury .panel,
.control-shell.theme-luxury .sponsor-panel {
  position: relative;
  color: #f8fafc;
  padding: clamp(28px, 5.5vw, 72px);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.095), rgba(255, 255, 255, 0.025)),
    rgba(6, 10, 22, 0.50);
  border: 1px solid rgba(255, 255, 255, 0.13);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.16),
    inset 0 -1px 0 rgba(255, 255, 255, 0.04),
    0 36px 120px rgba(0, 0, 0, 0.52),
    0 0 110px rgba(139, 92, 246, 0.13);
  backdrop-filter: blur(30px) saturate(155%);
  -webkit-backdrop-filter: blur(30px) saturate(155%);
  overflow: hidden;
  border-radius: 38px;
}

.control-shell.theme-luxury .now-playing {
  border-radius: 38px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.095), rgba(255, 255, 255, 0.025)),
    rgba(6, 10, 22, 0.50);
  border: 1px solid rgba(255, 255, 255, 0.13);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.16),
    inset 0 -1px 0 rgba(255, 255, 255, 0.04),
    0 36px 120px rgba(0, 0, 0, 0.52),
    0 0 110px rgba(139, 92, 246, 0.13);
  backdrop-filter: blur(30px) saturate(155%);
  -webkit-backdrop-filter: blur(30px) saturate(155%);
  padding: 18px;
  margin-bottom: 22px;
}

.control-shell.theme-luxury .hero-band {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

/* Specific radius overrides */
.theme-luxury .liquid-player {
  position: relative;
  border-radius: 22px;
  width: 520px;
  height: 150px;
  padding: 18px;
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr);
  gap: 14px;
  isolation: isolate;
  contain: paint;
  user-select: none;
  -webkit-user-select: none;
  color: #f8fafc;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.018)),
    rgba(15, 23, 42, 0.42);
  border: 1px solid rgba(148, 163, 184, 0.15);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 18px 48px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(22px) saturate(145%);
  -webkit-backdrop-filter: blur(22px) saturate(145%);
}

.theme-luxury .liquid-player.idle {
  background: rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.theme-luxury .liquid-player.position-mode {
  cursor: move;
  -webkit-app-region: drag;
}

/* Internal components for liquid player */
.theme-luxury .liquid-player .mini-artwork,
.theme-luxury .liquid-player .floating-copy,
.theme-luxury .liquid-player .drag-chip,
.theme-luxury .liquid-player .floating-progress {
  position: relative;
  z-index: 1;
}

.theme-luxury .liquid-player .floating-time {
  position: absolute;
  right: 19px;
  bottom: 22px;
  left: auto;
  color: #94a3b8;
  font-size: calc(11px * var(--player-text-scale));
  font-weight: 800;
  text-align: right;
}

.theme-luxury .liquid-player .mini-artwork {
  width: 84px;
  height: 84px;
  align-self: center;
  justify-self: start;
  border-radius: 14px;
  border-color: rgba(255, 255, 255, 0.13);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.02)),
    rgba(15, 23, 42, 0.2);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 8px 18px rgba(0, 0, 0, 0.26);
  backdrop-filter: blur(8px) saturate(1.25);
  -webkit-backdrop-filter: blur(8px) saturate(1.25);
}

.theme-luxury .liquid-player .floating-copy {
  min-width: 0;
  align-self: center;
  padding-top: 0;
}

.theme-luxury .liquid-player .floating-meta {
  gap: 8px;
  font-size: calc(11px * var(--player-text-scale));
  font-weight: 900;
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.5);
}

.theme-luxury .liquid-player .floating-meta strong {
  display: none;
}

.theme-luxury .liquid-player .floating-copy h1 {
  overflow: hidden;
  margin-top: 8px;
  color: #f8fafc;
  font-size: calc(18px * var(--player-text-scale));
  line-height: 1.25;
  font-weight: 780;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-luxury .liquid-player .floating-copy p {
  overflow: hidden;
  margin-top: 8px;
  color: #94a3b8;
  font-size: calc(14px * var(--player-text-scale));
  line-height: 1.2;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-luxury .liquid-player .combined-time {
  display: inline;
}

.theme-luxury .liquid-player .split-time {
  grid-column: 1 / 3;
  grid-row: 3;
  align-self: end;
  display: none;
  justify-content: space-between;
  color: #94a3b8;
  font-size: calc(11px * var(--player-text-scale));
  font-weight: 900;
}

.theme-luxury .liquid-player .floating-progress {
  position: absolute;
  right: 18px;
  bottom: 12px;
  left: 18px;
  overflow: visible;
  height: 5px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.6);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    inset 0 -1px 0 rgba(0, 0, 0, 0.18);
}

.theme-luxury .liquid-player .floating-progress div {
  min-width: 5px;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #38bdf8, #8b5cf6);
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
  transition: width 280ms linear;
  will-change: width;
}

.theme-luxury .liquid-player .progress-thumb {
  position: absolute;
  top: 50%;
  right: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #f8fafc;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.24);
  transform: translate(-50%, -50%);
  transition: left 680ms cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}

.theme-luxury .liquid-player .drag-chip {
  top: 10px;
  right: 12px;
  background: rgba(15, 23, 42, 0.52);
  color: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.23);
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
}

/* Control Shell Panels */
.control-shell.theme-luxury .panel::before,
.control-shell.theme-luxury .sponsor-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 255, 255, 0.12), transparent 28%),
    radial-gradient(circle at 88% 100%, rgba(139, 92, 246, 0.14), transparent 34%);
  opacity: 0.72;
}

.control-shell.theme-luxury .panel > *,
.control-shell.theme-luxury .sponsor-panel > * {
  position: relative;
  z-index: 1;
}

/* Eyebrow & Titles */
.control-shell.theme-luxury .eyebrow,
.control-shell.theme-luxury .guide-heading {
  width: fit-content;
  margin: 0 0 20px;
  padding: 9px 13px;
  border-radius: 999px;
  color: #c4b5fd;
  background: rgba(139, 92, 246, 0.12);
  border: 1px solid rgba(196, 181, 253, 0.17);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
  line-height: 1;
}

.control-shell.theme-luxury .hero-band h1 {
  max-width: 900px;
  margin: 0;
  font-size: clamp(38px, 6vw, 64px);
  line-height: 0.94;
  letter-spacing: -0.05em;
  font-weight: 800;
  color: transparent;
  background: linear-gradient(90deg, #f8fafc, #a78bfa 42%, #38bdf8 86%);
  background-clip: text;
  -webkit-background-clip: text;
}

.control-shell.theme-luxury .summary {
  max-width: 690px;
  margin: 24px 0 0;
  color: #94a3b8;
  font-size: clamp(16px, 1.9vw, 20px);
  line-height: 1.82;
}

/* Pills and Buttons */
.control-shell.theme-luxury .service-button,
.control-shell.theme-luxury .action-grid button,
.control-shell.theme-luxury .scale-control button,
.control-shell.theme-luxury .controller-customize-button,
.control-shell.theme-luxury .controller-reset-button,
.control-shell.theme-luxury .sponsor-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 12px 16px;
  border-radius: 999px;
  color: rgba(248, 250, 252, 0.90);
  background: rgba(15, 23, 42, 0.52);
  border: 1px solid rgba(148, 163, 184, 0.23);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 12px 34px rgba(0, 0, 0, 0.22);
  font-size: 14px;
  line-height: 1;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;
}

.control-shell.theme-luxury .action-grid button {
  min-height: 52px;
}

.control-shell.theme-luxury .service-button:hover,
.control-shell.theme-luxury .action-grid button:hover,
.control-shell.theme-luxury .scale-control button:hover,
.control-shell.theme-luxury .controller-customize-button:hover,
.control-shell.theme-luxury .controller-customize-button.listening,
.control-shell.theme-luxury .action-grid button.active,
.control-shell.theme-luxury .service-button.active-service,
.control-shell.theme-luxury .sponsor-button:hover {
  transform: translateY(-2px);
  background:
    linear-gradient(135deg, rgba(139, 92, 246, 0.62), rgba(56, 189, 248, 0.34)),
    rgba(15, 23, 42, 0.68);
  border-color: rgba(196, 181, 253, 0.28);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.10),
    0 16px 42px rgba(139, 92, 246, 0.20);
  color: #ffffff;
}

/* Status Pills */
.control-shell.theme-luxury .status-pill,
.control-shell.theme-luxury .theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  color: rgba(248, 250, 252, 0.92);
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-size: 14px;
}

.control-shell.theme-luxury .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #8b5cf6;
  box-shadow: 0 0 18px rgba(139, 92, 246, 0.9);
}

/* Typography Overrides */
.control-shell.theme-luxury .section-title h2,
.control-shell.theme-luxury .track-copy h2,
.control-shell.theme-luxury .sponsor-copy h2 {
  color: #f8fafc;
  font-size: 20px;
  letter-spacing: -0.03em;
  margin-top: 0;
  font-weight: 700;
}

.control-shell.theme-luxury .section-title p,
.control-shell.theme-luxury .track-copy p,
.control-shell.theme-luxury .sponsor-copy p:last-child {
  color: #94a3b8;
  line-height: 1.7;
}

/* Progress bar */
.control-shell.theme-luxury .progress-track {
  height: 6px;
  background: rgba(15, 23, 42, 0.52);
  border-radius: 999px;
}

.control-shell.theme-luxury .progress-fill {
  background: linear-gradient(90deg, #38bdf8, #8b5cf6);
  border-radius: 999px;
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.5);
}

.control-shell.theme-luxury .source-dot {
  background: #8b5cf6;
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.5);
}

/* Controller Prompt */
.control-shell.theme-luxury .gamepad-profile-prompt {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.62);
  border-radius: 12px;
  padding: 12px;
}

.control-shell.theme-luxury .gamepad-profile-prompt b {
  color: #f8fafc;
}

.control-shell.theme-luxury .controller-row {
  min-height: 44px;
  padding: 4px 8px;
  border: 1px solid rgba(148, 163, 184, 0.23);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.52);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.control-shell.theme-luxury .controller-row b {
  color: #f8fafc;
}

.control-shell.theme-luxury .shortcut-grid b {
  color: #f8fafc;
}

.control-shell.theme-luxury .shortcut-grid span {
  background: rgba(15, 23, 42, 0.52);
  border: 1px solid rgba(148, 163, 184, 0.23);
  color: #f8fafc;
}

.control-shell.theme-luxury .xbox-button-img {
  filter: drop-shadow(0 0 6px rgba(139, 92, 246, 0.4));
}

.control-shell.theme-luxury .toolbar-cluster {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 0;
}
"""

new_lines = lines[:start_idx] + [new_css + "\n"] + lines[end_idx:test_idx]

with codecs.open(css_path, 'w', 'utf-8') as f:
    f.writelines(new_lines)

print(f"Replaced lines {start_idx} to {end_idx} and removed test block after {test_idx}")
