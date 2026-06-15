import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Audio} from '@remotion/media';

const clamp = (value: number, from: number, to: number) =>
  interpolate(value, [from, to], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

const fadeWindow = (frame: number, duration: number, edge = 14) =>
  Math.min(clamp(frame, 0, edge), clamp(duration - frame, 0, edge));

const services = [
  {name: 'YOUTUBE MUSIC', color: '#ff174f'},
  {name: 'SPOTIFY', color: '#22dd73'},
  {name: 'APPLE MUSIC', color: '#f5f7ff'},
];

const track = {
  title: 'CELEBRATION',
  artist: 'LE SSERAFIM',
  time: '0:34 / 2:33',
};

const ParticleField: React.FC<{accent?: string; energy?: number}> = ({
  accent = '#49ecff',
  energy = 1,
}) => {
  const frame = useCurrentFrame();
  return (
    <div className="particles">
      {Array.from({length: 32}).map((_, index) => {
        const x = (index * 173) % 1920;
        const y = (index * 317) % 1080;
        const drift = ((frame * (0.35 + (index % 5) * 0.08)) % 180) * energy;
        const opacity = 0.14 + ((index * 29) % 40) / 100;
        return (
          <span
            key={index}
            style={{
              left: x,
              top: (y + drift) % 1120 - 40,
              opacity,
              backgroundColor: accent,
              boxShadow: `0 0 ${10 + energy * 18}px ${accent}`,
            }}
          />
        );
      })}
    </div>
  );
};

const SpeedLines: React.FC<{accent?: string}> = ({accent = '#6ceeff'}) => {
  const frame = useCurrentFrame();
  return (
    <div className="speed-lines">
      {Array.from({length: 18}).map((_, index) => {
        const offset = ((frame * (18 + index * 0.7) + index * 127) % 2300) - 200;
        const top = 90 + ((index * 71) % 900);
        return (
          <span
            key={index}
            style={{
              width: 150 + (index % 4) * 100,
              transform: `translateX(${offset}px)`,
              top,
              opacity: 0.12 + (index % 5) * 0.055,
              background: `linear-gradient(90deg, transparent, ${accent})`,
            }}
          />
        );
      })}
    </div>
  );
};

const BrandMark: React.FC<{small?: boolean}> = ({small = false}) => (
  <div className={`brand ${small ? 'brand-small' : ''}`}>
    <Img src={staticFile('logo-rounded.png')} />
    <div>
      <strong>FORZA MUSIC</strong>
      <span>懸浮播放器</span>
    </div>
  </div>
);

const AlbumArt: React.FC<{accent: string}> = ({accent}) => {
  const frame = useCurrentFrame();
  const rotation = interpolate(frame, [0, 180], [-7, 5], {
    extrapolateRight: 'extend',
  });
  return (
    <div className="album-shell" style={{borderColor: accent, boxShadow: `0 0 34px ${accent}77`}}>
      <div className="album-art" style={{transform: `rotate(${rotation}deg)`}}>
        <div className="album-horizon" />
        <div className="album-sun" style={{backgroundColor: accent}} />
        <div className="album-road" />
      </div>
    </div>
  );
};

const ElectricBorder: React.FC<{accent: string; energy?: number}> = ({accent, energy = 1}) => {
  const frame = useCurrentFrame();
  const pulse = 0.68 + Math.sin(frame / 3.2) * 0.15 * energy;
  return (
    <>
      <div
        className="electric-border"
        style={{
          borderColor: accent,
          opacity: pulse,
          boxShadow: `0 0 ${14 + energy * 20}px ${accent}, inset 0 0 ${12 + energy * 10}px ${accent}66`,
        }}
      />
      {Array.from({length: 10}).map((_, index) => (
        <span
          className="electric-notch"
          key={index}
          style={{
            left: `${6 + index * 9.8}%`,
            top: index % 2 === 0 ? -3 : 'auto',
            bottom: index % 2 === 0 ? 'auto' : -3,
            width: `${2 + ((frame + index) % 3)}%`,
            opacity: 0.45 + Math.sin(frame / 4 + index) * 0.25,
            backgroundColor: accent,
            boxShadow: `0 0 15px ${accent}`,
          }}
        />
      ))}
    </>
  );
};

const Waveform: React.FC<{accent: string; energy?: number}> = ({accent, energy = 1}) => {
  const frame = useCurrentFrame();
  return (
    <div className="waveform">
      {Array.from({length: 68}).map((_, index) => {
        const height =
          12 +
          Math.abs(Math.sin(index * 0.36 + frame * 0.12)) * 52 * energy +
          Math.abs(Math.cos(index * 0.11 + frame * 0.06)) * 20 * energy;
        return (
          <span
            key={index}
            style={{
              height,
              background: `linear-gradient(180deg, ${accent}, #55e6ff)`,
              boxShadow: `0 0 12px ${accent}`,
            }}
          />
        );
      })}
    </div>
  );
};

const PlayerCard: React.FC<{
  accent?: string;
  service?: string;
  compact?: boolean;
  glass?: boolean;
  energized?: boolean;
}> = ({
  accent = '#22dd73',
  service = 'SPOTIFY',
  compact = false,
  glass = false,
  energized = false,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame % 300, [0, 300], [22, 72]);
  const energy = energized ? 1.55 : 0.75;
  return (
    <div className={`player-card ${compact ? 'compact' : ''} ${glass ? 'glass' : ''}`}>
      {energized && <ElectricBorder accent={accent} energy={energy} />}
      <div className="player-top">
        <AlbumArt accent={accent} />
        <div className="track-copy">
          <div className="service-line" style={{color: accent}}>
            <i style={{backgroundColor: accent}} />
            {service}
          </div>
          <h2>{track.title}</h2>
          <p>{track.artist}</p>
        </div>
        <div className="volume-box" style={{borderColor: accent, color: accent}}>
          <span className="speaker-icon">◖</span>
          <b>86%</b>
        </div>
      </div>
      {!compact && <Waveform accent={accent} energy={energy} />}
      <div className="progress">
        <span style={{width: `${progress}%`, backgroundColor: accent, boxShadow: `0 0 16px ${accent}`}} />
      </div>
      <div className="time-line">
        <span>{track.time}</span>
        {!compact && <span className="lyric" style={{color: accent}}>(Eunchae) Time to celebrate</span>}
      </div>
    </div>
  );
};

const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const enter = clamp(frame, 0, 26);
  const leave = clamp(frame, 118, 146);
  const opacity = enter - leave;
  return (
    <AbsoluteFill className="scene dark-scene">
      <SpeedLines />
      <ParticleField />
      <div className="intro-grid" style={{opacity}} />
      <div
        className="intro-content"
        style={{
          opacity,
          transform: `translateY(${(1 - enter) * 42}px) scale(${0.94 + enter * 0.06})`,
        }}
      >
        <BrandMark />
        <p className="eyebrow">FORZA 專屬音樂體驗</p>
        <h1>把音樂留在<br /><em>賽道</em>裡。</h1>
        <p className="intro-sub">遊戲不中斷。音樂不離場。</p>
      </div>
      <div className="road-glow" />
    </AbsoluteFill>
  );
};

const InGameOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 210;
  const opacity = fadeWindow(frame, duration);
  const cardEnter = clamp(frame, 18, 52);
  return (
    <AbsoluteFill className="scene cockpit-scene" style={{opacity}}>
      <SpeedLines accent="#32dfff" />
      <ParticleField accent="#2cf1ce" />
      <div className="horizon-glow" />
      <div className="mock-road">
        <span />
        <span />
      </div>
      <div className="car-hood" />
      <div className="hud-speed"><b>238</b><span>KM/H</span></div>
      <div className="scene-label">
        <span>01</span>
        <div><b>不必切出遊戲</b><small>正在播放的歌，留在視線內</small></div>
      </div>
      <div
        className="overlay-demo"
        style={{
          opacity: cardEnter,
          transform: `translate(${(1 - cardEnter) * -55}px, ${(1 - cardEnter) * -20}px) scale(${0.88 + cardEnter * 0.12})`,
        }}
      >
        <PlayerCard compact accent="#ff174f" service="YOUTUBE MUSIC" />
      </div>
    </AbsoluteFill>
  );
};

const ServiceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 210;
  const opacity = fadeWindow(frame, duration);
  const index = Math.min(2, Math.floor(frame / 62));
  const service = services[index];
  const serviceEnter = clamp(frame % 62, 0, 18);
  return (
    <AbsoluteFill className="scene panel-scene" style={{opacity}}>
      <ParticleField accent={service.color} energy={0.8} />
      <BrandMark small />
      <div className="scene-heading">
        <p className="eyebrow">一個播放器。三個服務。</p>
        <h2>你常用的音樂，<br />都能上車。</h2>
      </div>
      <div className="service-list">
        {services.map((item, serviceIndex) => (
          <div className={`service-pill ${index === serviceIndex ? 'active' : ''}`} key={item.name}>
            <i style={{backgroundColor: item.color, boxShadow: `0 0 18px ${item.color}`}} />
            <span>{item.name}</span>
          </div>
        ))}
      </div>
      <div
        className="feature-player"
        style={{
          opacity: serviceEnter,
          transform: `translateX(${(1 - serviceEnter) * 60}px)`,
        }}
      >
        <PlayerCard accent={service.color} service={service.name} />
      </div>
    </AbsoluteFill>
  );
};

const ModeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 210;
  const opacity = fadeWindow(frame, duration);
  const glass = frame > 64;
  const energized = frame > 128;
  const accent = energized ? '#57ffae' : glass ? '#ff93d6' : '#ff174f';
  const mode = energized ? 'BORDERLESS RADIO' : glass ? 'LIQUID GLASS' : 'DARK MODE';
  return (
    <AbsoluteFill className={`scene mode-scene ${glass ? 'mode-glass' : ''}`} style={{opacity}}>
      <ParticleField accent={accent} energy={energized ? 1.6 : 0.8} />
      <SpeedLines accent={accent} />
      <div className="scene-heading compact-heading">
        <p className="eyebrow">自由切換視覺風格</p>
        <h2>{mode}</h2>
        <small>從安靜、透亮，到賽道高能狀態。</small>
      </div>
      <div className="mode-tabs">
        {['DARK', 'GLASS', 'RADIO'].map((item, index) => (
          <span className={(frame < 64 ? index === 0 : frame < 128 ? index === 1 : index === 2) ? 'selected' : ''} key={item}>
            {item}
          </span>
        ))}
      </div>
      <div className="center-player">
        <PlayerCard accent={accent} service="SPOTIFY" glass={glass} energized={energized} />
      </div>
    </AbsoluteFill>
  );
};

const KeyCombo: React.FC<{button: string; label: string; delay: number}> = ({button, label, delay}) => {
  const frame = useCurrentFrame();
  const enter = clamp(frame, delay, delay + 22);
  const filename = button === 'A' ? 'xbox-a.svg' : button === 'B' ? 'xbox-b.svg' : 'xbox-x.svg';
  return (
    <div className="combo" style={{opacity: enter, transform: `translateY(${(1 - enter) * 20}px)`}}>
      <Img className="stick" src={staticFile('xbox-l3.png')} />
      <b>+</b>
      <Img className="face-button" src={staticFile(filename)} />
      <span>{label}</span>
    </div>
  );
};

const ControlScene: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 210;
  const opacity = fadeWindow(frame, duration);
  return (
    <AbsoluteFill className="scene control-scene" style={{opacity}}>
      <ParticleField accent="#9d70ff" energy={0.9} />
      <div className="scene-heading">
        <p className="eyebrow">不用離開方向盤</p>
        <h2>手把與鍵盤<br /><em>即時控制</em></h2>
        <small>快捷鍵可依習慣自訂，避免重複設定。</small>
      </div>
      <div className="combo-panel">
        <KeyCombo button="A" label="播放 / 暫停" delay={18} />
        <KeyCombo button="B" label="下一首" delay={42} />
        <KeyCombo button="X" label="上一首" delay={66} />
      </div>
      <div className="keyboard-panel">
        <span>CTRL + ALT + P</span>
        <b>拖曳調整懸浮位置</b>
        <span>60% - 100%</span>
        <b>播放器尺寸自由縮放</b>
      </div>
    </AbsoluteFill>
  );
};

const GearScene: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 240;
  const opacity = fadeWindow(frame, duration);
  const gear = Math.min(6, 2 + Math.floor(frame / 40));
  const energy = 0.8 + gear * 0.13;
  const flash = clamp(frame % 40, 0, 7) - clamp(frame % 40, 12, 24);
  return (
    <AbsoluteFill className="scene gear-scene" style={{opacity}}>
      <ParticleField accent="#58ffb2" energy={energy} />
      <SpeedLines accent="#58ffb2" />
      <div className="gear-heading">
        <p className="eyebrow">FORZA UDP TELEMETRY</p>
        <h2>換檔，讓播放器<br /><em>進化。</em></h2>
        <small>車速與檔位越高，氣場越強。</small>
      </div>
      <div className="gear-player" style={{transform: `scale(${0.92 + flash * 0.035})`}}>
        <PlayerCard accent="#57ffae" service="SPOTIFY" energized />
      </div>
      <div className="gear-meter">
        <span>GEAR</span><b>{gear}</b><small>{Math.round(142 + frame * 0.48)} KM/H</small>
      </div>
      <div className="gear-flash" style={{opacity: flash * 0.22}} />
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = clamp(frame, 0, 28);
  const logoScale = interpolate(frame, [0, 38], [0.82, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill className="scene outro-scene">
      <ParticleField accent="#57dff5" energy={0.75} />
      <SpeedLines accent="#57dff5" />
      <div className="outro-content" style={{opacity}}>
        <Img className="outro-logo" src={staticFile('logo-rounded.png')} style={{transform: `scale(${logoScale})`}} />
        <p className="eyebrow">FORZA MUSIC OVERLAY</p>
        <h2>你的音樂。<br />你的賽道。</h2>
        <p className="outro-copy">免費下載 Windows 版</p>
        <div className="download-chip">github.com/scott0127/forza-horizon-6-youtube-muisc-player</div>
        <div className="outro-footer"><span>Scott Lin 2026</span><span>v3.5</span></div>
      </div>
    </AbsoluteFill>
  );
};

export const PromoVideo: React.FC = () => (
  <AbsoluteFill className="video-root">
    <Audio
      src={staticFile('promo-pulse.wav')}
      volume={(frame) => interpolate(frame, [0, 18, 1510, 1619], [0, 0.52, 0.52, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })}
    />
    <Sequence from={0} durationInFrames={150} premountFor={30}><Intro /></Sequence>
    <Sequence from={138} durationInFrames={210} premountFor={30}><InGameOverlay /></Sequence>
    <Sequence from={330} durationInFrames={210} premountFor={30}><ServiceScene /></Sequence>
    <Sequence from={522} durationInFrames={210} premountFor={30}><ModeScene /></Sequence>
    <Sequence from={714} durationInFrames={210} premountFor={30}><ControlScene /></Sequence>
    <Sequence from={906} durationInFrames={240} premountFor={30}><GearScene /></Sequence>
    <Sequence from={1128} durationInFrames={492} premountFor={30}><Outro /></Sequence>
  </AbsoluteFill>
);
