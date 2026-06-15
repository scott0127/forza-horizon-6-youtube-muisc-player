import React from 'react';
import {Audio} from '@remotion/media';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import './demo-style.css';

const ease = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

const RaceBackdrop: React.FC<{muted?: boolean; boost?: number}> = ({
  muted = false,
  boost = 0,
}) => {
  const frame = useCurrentFrame();
  return (
    <div className={`demo-race ${muted ? 'is-muted' : ''}`}>
      <div className="demo-sky" />
      <div className="demo-mountains demo-mountains-back" />
      <div className="demo-mountains demo-mountains-front" />
      <div className="demo-city">
        {Array.from({length: 19}).map((_, index) => (
          <span
            key={index}
            style={{
              left: `${index * 5.8}%`,
              height: `${28 + ((index * 17) % 58)}px`,
            }}
          />
        ))}
      </div>
      <div className="demo-road">
        <div className="demo-road-edge left" />
        <div className="demo-road-edge right" />
        {Array.from({length: 13}).map((_, index) => {
          const travel = (frame * (10 + boost * 7) + index * 93) % 1120;
          const y = 328 + travel * 0.74;
          const width = 6 + travel * 0.035;
          return (
            <span
              className="demo-road-dash"
              key={index}
              style={{
                top: y,
                width,
                height: 12 + travel * 0.035,
                marginLeft: -width / 2,
              }}
            />
          );
        })}
      </div>
      <div className="demo-car">
        <span className="demo-tail-light left" />
        <span className="demo-tail-light right" />
        <span className="demo-license">SCOTT 26</span>
      </div>
      <div className="demo-speed-lines">
        {Array.from({length: 24}).map((_, index) => {
          const x = ((frame * (15 + boost * 17) + index * 147) % 2400) - 260;
          return (
            <span
              key={index}
              style={{
                top: `${6 + ((index * 37) % 88)}%`,
                width: `${100 + (index % 5) * 42}px`,
                transform: `translateX(${x}px)`,
                opacity: 0.1 + boost * 0.09,
              }}
            />
          );
        })}
      </div>
    </div>
  );
};

const MusicBrowser: React.FC = () => {
  const frame = useCurrentFrame();
  const show = ease(frame, 18, 38);
  const freeze = ease(frame, 46, 62);
  return (
    <>
      <div
        className="demo-browser"
        style={{
          opacity: show,
          transform: `translateY(${(1 - show) * 80}px) scale(${0.92 + show * 0.08})`,
        }}
      >
        <div className="demo-browser-tabs">
          <span className="demo-browser-dot red" />
          <span className="demo-browser-dot amber" />
          <span className="demo-browser-dot green" />
          <b>YouTube Music</b>
        </div>
        <div className="demo-browser-body">
          <div className="demo-browser-side">
            <strong>Music</strong>
            <span>首頁</span>
            <span>探索</span>
            <span>媒體庫</span>
          </div>
          <div className="demo-browser-content">
            <div className="demo-browser-cover" />
            <p>正在播放</p>
            <h2>CELEBRATION</h2>
            <small>LE SSERAFIM</small>
            <div className="demo-browser-progress"><i /></div>
            <div className="demo-browser-controls">◀　❚❚　▶</div>
          </div>
        </div>
      </div>
      <div className="demo-paused" style={{opacity: freeze}}>
        <strong>PAUSED</strong>
        <span>遊戲被迫中斷</span>
      </div>
      <div className="demo-friction-copy" style={{opacity: ease(frame, 36, 54)}}>
        <small>每次換歌都要</small>
        <b>切出遊戲？</b>
      </div>
    </>
  );
};

type Track = {
  title: string;
  artist: string;
  service: string;
  accent: string;
  time: string;
  progress: number;
};

const RadioPlayer: React.FC<{track: Track; swap: number}> = ({track, swap}) => {
  const frame = useCurrentFrame();
  const breathe = 0.74 + Math.sin(frame / 10) * 0.13;
  const smokeX = 150 - ((frame * 3.4) % 310);
  return (
    <div className="demo-radio" style={{'--demo-accent': track.accent} as React.CSSProperties}>
      <div
        className="demo-radio-pulse"
        style={{
          opacity: breathe * 0.42,
          transform: `translate(-50%, -50%) scale(${1 + breathe * 0.23})`,
        }}
      />
      <div className="demo-radio-artwork">
        <div className="demo-radio-artwork-sky" />
        <div className="demo-radio-artwork-road" />
      </div>
      <div className="demo-radio-body">
        <div className="demo-radio-freq">
          <i />
          <span>{track.service}</span>
        </div>
        <div
          className="demo-radio-track"
          style={{
            opacity: 1 - swap * 0.76,
            transform: `translateY(${swap * -8}px)`,
          }}
        >
          <strong>{track.title}</strong>
          <span>{track.artist}</span>
        </div>
        <div
          className="demo-radio-smoke"
          style={{
            backgroundPosition: `${smokeX}% 0`,
            opacity: 0.68 + breathe * 0.18,
          }}
        />
      </div>
      <span className="demo-radio-time">{track.time}</span>
      <div className="demo-radio-progress">
        <i style={{width: `${track.progress}%`}} />
      </div>
    </div>
  );
};

const ControllerCombo: React.FC<{opacity: number}> = ({opacity}) => {
  const frame = useCurrentFrame();
  const press = ease(frame, 164, 173) - ease(frame, 181, 190);
  return (
    <div
      className="demo-controller"
      style={{
        opacity,
        transform: `translateY(${(1 - opacity) * 34}px) scale(${1 + press * 0.035})`,
      }}
    >
      <div className="demo-controller-copy">
        <small>遊戲中直接操作</small>
        <b>L3 + B</b>
        <span>下一首</span>
      </div>
      <div className="demo-controller-buttons">
        <Img src={staticFile('xbox-l3.png')} />
        <b>+</b>
        <Img src={staticFile('xbox-b.svg')} />
      </div>
    </div>
  );
};

const Solution: React.FC = () => {
  const frame = useCurrentFrame();
  const reveal = ease(frame, 112, 140);
  const combo = ease(frame, 145, 164);
  const swapOut = ease(frame, 165, 177);
  const swapIn = ease(frame, 177, 194);
  const switched = frame >= 177;
  const track: Track = switched
    ? {
        title: 'DRIVE INTO THE NIGHT',
        artist: 'SCOTT LIN RADIO',
        service: 'SPOTIFY',
        accent: '#22dd73',
        time: '0:01 / 3:42',
        progress: 2,
      }
    : {
        title: 'CELEBRATION',
        artist: 'LE SSERAFIM',
        service: 'YOUTUBE MUSIC',
        accent: '#ff174f',
        time: '0:34 / 2:33',
        progress: 23,
      };
  const swap = switched ? 1 - swapIn : swapOut;
  return (
    <div className="demo-solution" style={{opacity: reveal}}>
      <div className="demo-solution-heading">
        <small>FORZA MUSIC OVERLAY</small>
        <b>音樂留在賽道裡。</b>
      </div>
      <div
        className="demo-radio-wrap"
        style={{
          transform: `translateX(${(1 - reveal) * -80}px) scale(${0.92 + reveal * 0.08})`,
        }}
      >
        <RadioPlayer track={track} swap={swap} />
      </div>
      <ControllerCombo opacity={combo} />
      <div className="demo-lyric" style={{opacity: ease(frame, 202, 225)}}>
        <span>(Eunchae)</span> Time to celebrate, time to celebrate
      </div>
    </div>
  );
};

export const DemoVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const wipe = ease(frame, 91, 126);
  return (
    <AbsoluteFill className="demo-root">
      <Audio
        src={staticFile('promo-pulse.wav')}
        volume={(audioFrame) =>
          interpolate(audioFrame, [0, 14, 298], [0, 0.45, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })
        }
      />
      <RaceBackdrop muted={frame < 110} boost={wipe} />
      {frame < 128 && <MusicBrowser />}
      {frame >= 92 && <Solution />}
      <div
        className="demo-neon-wipe"
        style={{
          transform: `translateX(${interpolate(wipe, [0, 1], [-145, 310])}%) skewX(-13deg)`,
        }}
      />
      <div className="demo-vignette" />
    </AbsoluteFill>
  );
};
