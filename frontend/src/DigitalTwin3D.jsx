import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function DigitalTwin3D({ telemetry, status }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene setup
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0f172a, 0.05);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(3, 2, 5);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00f2fe, 3, 10);
    pointLight.position.set(2, 3, 2);
    scene.add(pointLight);

    // 3D Digital Twin Model Construction (Machinery Cylinder + Core Sphere + Rotor Fins)
    const group = new THREE.Group();

    // Outer Chassis Mesh
    const chassisGeo = new THREE.CylinderGeometry(1.2, 1.2, 2.2, 32, 1, true);
    const chassisMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      metalness: 0.8,
      roughness: 0.2,
      wireframe: true,
      transparent: true,
      opacity: 0.6
    });
    const chassis = new THREE.Mesh(chassisGeo, chassisMat);
    group.add(chassis);

    // Glowing Inner Sensor Core
    const coreGeo = new THREE.SphereGeometry(0.7, 32, 32);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x00f2fe,
      emissive: 0x00f2fe,
      emissiveIntensity: 0.8,
      roughness: 0.1
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    group.add(core);

    // Rotor Fins
    const finGeo = new THREE.BoxGeometry(2.2, 0.08, 0.3);
    const finMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9 });
    for (let i = 0; i < 3; i++) {
      const fin = new THREE.Mesh(finGeo, finMat);
      fin.rotation.y = (Math.PI / 3) * i;
      fin.position.y = 0.8;
      group.add(fin);
    }

    scene.add(group);

    // Animation Loop
    let animationFrameId;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Rotate twin based on temperature/speed
      const speed = telemetry?.temperature ? Math.min(0.05, telemetry.temperature * 0.001) : 0.01;
      group.rotation.y += speed;

      // Update color based on temperature/status
      const temp = telemetry?.temperature || 22.0;
      if (temp > 30) {
        coreMat.color.setHex(0xef4444);
        coreMat.emissive.setHex(0xef4444);
        pointLight.color.setHex(0xef4444);
      } else if (temp > 25) {
        coreMat.color.setHex(0xf59e0b);
        coreMat.emissive.setHex(0xf59e0b);
        pointLight.color.setHex(0xf59e0b);
      } else {
        coreMat.color.setHex(0x00f2fe);
        coreMat.emissive.setHex(0x00f2fe);
        pointLight.color.setHex(0x00f2fe);
      }

      renderer.render(scene, camera);
    };

    animate();

    // Handle Window Resize
    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth;
      const newH = container.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [telemetry]);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
}
