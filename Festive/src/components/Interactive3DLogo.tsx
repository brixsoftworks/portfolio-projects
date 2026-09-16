'use client';

import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';

const vertexShader = `
varying vec2 vUv;
void main() {
  vUv = uv;
  // Position the plane to exactly fill the orthographic-like view
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const fragmentShader = `
uniform sampler2D uImage;
uniform sampler2D uDepth;
uniform vec2 uMouse;
uniform float uHover;
varying vec2 vUv;

void main() {
  vec4 depthColor = texture2D(uDepth, vUv);
  // depth Color is grayscale
  float depth = depthColor.r;
  
  // Parallax intensity
  float intensity = 0.05 * uHover;
  
  // Calculate displacement
  // Map depth from [0, 1] to [-0.5, 0.5] so mid-depth is neutral
  vec2 displacement = vec2(uMouse.x, uMouse.y) * (depth - 0.5) * intensity;
  
  // Sample the image with displacement
  // Add a slight zoom to hide the edges when displacing
  vec2 zoomedUv = (vUv - 0.5) * (1.0 - (0.05 * uHover)) + 0.5;
  vec4 color = texture2D(uImage, zoomedUv + displacement);
  
  gl_FragColor = color;
}
`;

interface SceneProps {
  imagePath: string;
  depthPath: string;
  isHovered: boolean;
}

function Scene({ imagePath, depthPath, isHovered }: SceneProps) {
  const [image, depth] = useTexture([imagePath, depthPath]);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uImage: { value: image },
      uDepth: { value: depth },
      uMouse: { value: new THREE.Vector2(0, 0) },
      uHover: { value: 0 },
    }),
    [image, depth]
  );

  useFrame((state) => {
    if (materialRef.current) {
      // Smoothly interpolate mouse position
      materialRef.current.uniforms.uMouse.value.lerp(
        new THREE.Vector2(state.pointer.x, state.pointer.y),
        0.1
      );
      
      // Smoothly interpolate hover state
      const targetHover = isHovered ? 1 : 0;
      materialRef.current.uniforms.uHover.value += (targetHover - materialRef.current.uniforms.uHover.value) * 0.1;
    }
  });

  return (
    <mesh>
      {/* 2x2 plane fills the view when camera is at z=1 and fov=90 */}
      <planeGeometry args={[2, 2]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}

interface Interactive3DLogoProps {
  imagePath: string;
  depthPath: string;
  alt: string;
}

export default function Interactive3DLogo({ imagePath, depthPath, alt }: Interactive3DLogoProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="w-full h-full relative overflow-hidden rounded-xl"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label={alt}
    >
      {/* Fallback image shown before Canvas loads or if JS is disabled */}
      <img 
        src={imagePath} 
        alt={alt} 
        className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300 pointer-events-none" 
        style={{ opacity: isHovered ? 0 : 1 }}
      />
      
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
        <Canvas
          camera={{ position: [0, 0, 1], fov: 90 }}
          gl={{ alpha: true, antialias: false }}
          style={{ width: '100%', height: '100%' }}
        >
          <React.Suspense fallback={null}>
            <Scene imagePath={imagePath} depthPath={depthPath} isHovered={isHovered} />
          </React.Suspense>
        </Canvas>
      </div>
    </div>
  );
}
