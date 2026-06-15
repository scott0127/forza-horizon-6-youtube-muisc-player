import React from 'react';
import {Composition} from 'remotion';
import {PromoVideo} from './PromoVideo';
import {DemoVideo} from './DemoVideo';
import './style.css';

export const FPS = 30;
export const DURATION = 54 * FPS;

export const Root: React.FC = () => (
  <>
    <Composition
      id="GamingMusicPromo"
      component={PromoVideo}
      durationInFrames={DURATION}
      fps={FPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="GamingMusicDemo10s"
      component={DemoVideo}
      durationInFrames={10 * FPS}
      fps={FPS}
      width={1920}
      height={1080}
    />
  </>
);

