import { useRef, useMemo } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { Float, MeshDistortMaterial } from "@react-three/drei"
import * as THREE from "three"

function ParticleField() {
  const count = 2000
  const meshRef = useRef<THREE.Points>(null)
  const { pointer } = useThree()

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const col = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const i3 = i * 3
      const radius = 15 + Math.random() * 35
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      pos[i3] = radius * Math.sin(phi) * Math.cos(theta)
      pos[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      pos[i3 + 2] = radius * Math.cos(phi)
      const b = 0.3 + Math.random() * 0.7
      col[i3] = b
      col[i3 + 1] = b * (0.7 + Math.random() * 0.3)
      col[i3 + 2] = b * (0.5 + Math.random() * 0.3)
    }
    return [pos, col]
  }, [])

  useFrame((state) => {
    if (!meshRef.current) return
    const t = state.clock.elapsedTime * 0.06
    meshRef.current.rotation.x = Math.sin(t * 0.3) * 0.1 + pointer.y * 0.03
    meshRef.current.rotation.y = t * 0.12 + pointer.x * 0.03
  })

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.12} vertexColors transparent opacity={0.7} sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  )
}

function FloatingTorusKnot() {
  const meshRef = useRef<THREE.Mesh>(null)
  const { pointer } = useThree()

  useFrame((state) => {
    if (!meshRef.current) return
    const t = state.clock.elapsedTime
    meshRef.current.rotation.x = t * 0.12 + pointer.y * 0.4
    meshRef.current.rotation.y = t * 0.18 + pointer.x * 0.4
    meshRef.current.position.x = Math.sin(t * 0.15) * 0.8
    meshRef.current.position.y = Math.cos(t * 0.2) * 0.5
  })

  return (
    <mesh ref={meshRef} position={[0, 0, -8]}>
      <torusKnotGeometry args={[1.5, 0.5, 128, 16]} />
      <MeshDistortMaterial color="#e8b840" transparent opacity={0.1} wireframe distort={0.15} speed={2} />
    </mesh>
  )
}

function OrbitingRings() {
  const groupRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (!groupRef.current) return
    groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.08) * 0.25
    groupRef.current.rotation.y = state.clock.elapsedTime * 0.08
  })

  const rings = useMemo(() => {
    return Array.from({ length: 5 }, (_, i) => ({
      radius: 2.5 + i * 0.8,
      color: new THREE.Color().setHSL(0.1 + i * 0.01, 0.7, 0.4 + i * 0.08),
      opacity: 0.05 + i * 0.012,
      tilt: (i - 2) * 0.15,
    }))
  }, [])

  return (
    <group ref={groupRef} position={[0, 0, -6]}>
      {rings.map((ring, i) => (
        <mesh key={i} position={[0, 0, 0]} rotation={[ring.tilt, 0, 0]}>
          <ringGeometry args={[ring.radius, ring.radius + 0.02, 64]} />
          <meshBasicMaterial color={ring.color} transparent opacity={ring.opacity} side={THREE.DoubleSide} depthWrite={false} />
        </mesh>
      ))}
    </group>
  )
}

function FloatingShapes() {
  const groupRef = useRef<THREE.Group>(null)

  const shapes = useMemo(() => {
    const items = []
    const geometries = [
      <boxGeometry args={[1, 1, 1]} />,
      <octahedronGeometry args={[0.7]} />,
      <icosahedronGeometry args={[0.5]} />,
      <dodecahedronGeometry args={[0.6]} />,
    ]
    for (let i = 0; i < 8; i++) {
      items.push({
        position: [
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 12,
          -6 - Math.random() * 12,
        ] as [number, number, number],
        scale: 0.4 + Math.random() * 0.6,
        speed: 0.15 + Math.random() * 0.3,
        geometry: geometries[Math.floor(Math.random() * geometries.length)],
        color: new THREE.Color().setHSL(0.08 + Math.random() * 0.06, 0.7, 0.45 + Math.random() * 0.2),
        rotY: Math.random() * Math.PI * 2,
      })
    }
    return items
  }, [])

  useFrame((state) => {
    if (!groupRef.current) return
    groupRef.current.children.forEach((child, i) => {
      const s = shapes[i]
      child.rotation.x += 0.002
      child.rotation.y += 0.003
      child.position.y += Math.sin(state.clock.elapsedTime * s.speed + i * 1.5) * 0.002
    })
  })

  return (
    <group ref={groupRef}>
      {shapes.map((shape, i) => (
        <Float key={i} speed={shape.speed} floatIntensity={0.4} rotationIntensity={0.1}>
          <mesh position={shape.position} scale={shape.scale}>
            {shape.geometry}
            <MeshDistortMaterial color={shape.color} transparent opacity={0.08} wireframe distort={0.15} speed={1.5} />
          </mesh>
        </Float>
      ))}
    </group>
  )
}

function GlowingCenter() {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (!meshRef.current) return
    meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 0.4) * 0.06)
  })

  return (
    <mesh ref={meshRef} position={[0, 0, -10]}>
      <sphereGeometry args={[2, 32, 32]} />
      <MeshDistortMaterial color="#e8b840" transparent opacity={0.06} distort={0.4} speed={1.5} blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  )
}

function Scene() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={0.5} color="#e8b840" />
      <ParticleField />
      <FloatingTorusKnot />
      <OrbitingRings />
      <FloatingShapes />
      <GlowingCenter />
    </>
  )
}

export default function ThreeBackground() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 14], fov: 60 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }} style={{ background: "transparent" }}>
        <Scene />
      </Canvas>
    </div>
  )
}
