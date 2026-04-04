'use client';

import { motion, useScroll, useTransform, MotionValue } from 'framer-motion';
import { useRef } from 'react';
import { Scale } from 'lucide-react';
import Image from 'next/image';

interface LaptopScrollProps {
  children: React.ReactNode;
}

export function LaptopScroll({ children }: LaptopScrollProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });

  // Scale and rotate the laptop to "open" as user scrolls in the first 20%
  const scale = useTransform(scrollYProgress, [0, 0.15], [0.8, 1]);
  const rotateX = useTransform(scrollYProgress, [0, 0.15], [30, 0]);
  const yOffset = useTransform(scrollYProgress, [0, 0.15], ['30vh', '0vh']);

  // Opacity for the "Justice Democratized" text to fade out
  const titleOpacity = useTransform(scrollYProgress, [0, 0.1], [1, 0]);
  const titleY = useTransform(scrollYProgress, [0, 0.1], ['0vh', '-10vh']);

  return (
    <div ref={containerRef} className="relative w-full h-[400vh] bg-transparent">

      {/* Background glowing effects that stay constant or subtly shift */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px]" />
      </div>

      <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden">

        {/* Main Hero Text (Fades out quickly) */}
        <motion.div
          style={{ opacity: titleOpacity, y: titleY }}
          className="absolute w-full flex flex-col items-center justify-center text-center px-4 top-0 pt-[10vh] md:pt-[12vh] z-10"
        >
          <motion.div
            initial={{ opacity: 0, y: 40, filter: 'blur(20px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center"
          >
            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-indigo-500/40 bg-indigo-500/10 text-indigo-200 text-sm font-medium mb-8 backdrop-blur-md shadow-[0_0_30px_rgba(99,102,241,0.2)]">
              The Future of Legal Assistance in India
            </div>
            <h1 className="text-6xl md:text-[6.5rem] font-extrabold tracking-tighter mb-4 leading-[1.05] drop-shadow-2xl">
              Justice, <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-b from-indigo-300 via-purple-400 to-indigo-600 drop-shadow-[0_0_40px_rgba(99,102,241,0.6)]">
                Democratized.
              </span>
            </h1>
          </motion.div>
        </motion.div>

        {/* 3D Laptop Container */}
        <motion.div
          style={{ scale, rotateX, y: yOffset, perspective: "1000px" }}
          className="relative w-[90vw] md:w-[70vw] lg:w-[1000px] max-w-6xl aspect-[16/10]"
        >
          {/* Top bezel / screen casing */}
          <div className="absolute inset-0 bg-[#0f111a] border-[3px] border-[#3a3d4c] rounded-[24px] shadow-[0_0_100px_rgba(99,102,241,0.3)] overflow-hidden flex flex-col items-center pt-2 backdrop-blur-xl">

            {/* Webcam dot */}
            <div className="w-2 h-2 bg-black rounded-full mb-2 shadow-[inset_0_2px_4px_rgba(0,0,0,1)]" />

            {/* The actual Screen Content area */}
            <div className="relative w-[98%] max-w-[960px] h-full mb-4 bg-[#030305]/90 rounded-[14px] overflow-hidden border border-white/10 shadow-[inset_0_0_80px_rgba(99,102,241,0.05)] backdrop-blur-2xl">
              {children}
            </div>

          </div>

          {/* Bottom chassis of laptop */}
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-[110%] h-8 bg-gradient-to-b from-[#1a1c23] to-[#0a0b0e] rounded-b-[40px] shadow-[0_20px_40px_rgba(0,0,0,0.8)] flex justify-center pt-2 border-t border-[#3a3d4c] overflow-hidden">
            {/* Trackpad indent */}
            <div className="w-24 h-4 bg-[#11131a] rounded-t-lg shadow-inner" />
          </div>

        </motion.div>

      </div>
    </div>
  );
}

// Helper component to render the different "slides" inside the laptop screen based on scroll progress
export function ScrollContentBlocks({ scrollYProgress }: { scrollYProgress: MotionValue<number> }) {

  // Step 0: Initial Screen (Visible at start)
  const opacity0 = useTransform(scrollYProgress, [0, 0.05], [1, 0]);
  const y0 = useTransform(scrollYProgress, [0, 0.05], [0, -40]);

  // Step 1: Meet
  const opacity1 = useTransform(scrollYProgress, [0.1, 0.25, 0.35], [0, 1, 0]);
  const y1 = useTransform(scrollYProgress, [0.1, 0.25, 0.35], [40, 0, -40]);

  // Step 2: Citing Laws
  const opacity2 = useTransform(scrollYProgress, [0.35, 0.5, 0.6], [0, 1, 0]);
  const y2 = useTransform(scrollYProgress, [0.35, 0.5, 0.6], [40, 0, -40]);

  // Step 3: Drafting
  const opacity3 = useTransform(scrollYProgress, [0.6, 0.75, 1], [0, 1, 1]); // Final state stays visible
  const y3 = useTransform(scrollYProgress, [0.6, 0.75, 1], [40, 0, 0]);

  return (
    <div className="relative w-full h-full p-8 md:p-12 overflow-hidden flex flex-col justify-center">

      {/* Slide 0: Initial Dashboard */}
      <motion.div style={{ opacity: opacity0, y: y0, pointerEvents: 'none' }} className="absolute inset-0 p-12 flex flex-col items-center justify-center text-center">
        <div className="w-20 h-20 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6 border border-indigo-500/30">
          <Scale className="w-10 h-10 text-indigo-400" />
        </div>
        <h3 className="text-3xl font-semibold text-white mb-3 tracking-tight">Nyaya Sahayaka OS</h3>
        <p className="text-lg text-white/50 font-light mb-8">System Initialized and Ready.</p>

        <div className="flex gap-3">
          <div className="w-16 h-1.5 bg-indigo-500/30 rounded-full overflow-hidden relative">
            <motion.div
              className="absolute top-0 left-0 h-full w-full bg-indigo-400"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
            />
          </div>
          <div className="w-16 h-1.5 bg-purple-500/30 rounded-full overflow-hidden relative">
            <motion.div
              className="absolute top-0 left-0 h-full w-full bg-purple-400"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "linear", delay: 0.5 }}
            />
          </div>
        </div>
      </motion.div>

      {/* Slide 1: Welcome Dashboard */}
      <motion.div style={{ opacity: opacity1, y: y1 }} className="absolute inset-0 p-12 flex items-center justify-between text-left">
        <div className="w-1/2 pr-8">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="bg-indigo-500/20 p-2 rounded-lg"><Scale className="w-6 h-6 text-indigo-400" /></div>
            <span className="text-2xl font-semibold text-white">Nyaya Sahayaka</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">
            Breaking Language Barriers.
          </h2>
          <p className="text-xl text-white/50 max-w-2xl font-light mb-8">
            The legal system shouldn&apos;t be gated by English. Communicate naturally in Hindi, Bengali, Tamil, Telugu, Odia, or Marathi.
          </p>

          {/* Mock UI Element - Intense Glassmorphism */}
          <div className="w-full max-w-lg bg-white/[0.03] border border-white/10 rounded-[24px] p-6 backdrop-blur-xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-1/4 w-1/2 h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50" />
            <div className="flex gap-4 items-center mb-6">
              <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 border border-indigo-500/30">अ</div>
              <div className="bg-[#1a1d27]/80 rounded-2xl p-4 border border-white/5 text-[15px] text-white/80 tracking-wide">
                मुझे किरायेनामे से जुड़ी कानूनी सलाह चाहिए...
              </div>
            </div>
            <div className="flex gap-4 items-center flex-row-reverse">
              <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center border border-purple-500/30"><Scale className="w-5 h-5 text-purple-400" /></div>
              <div className="bg-indigo-500/10 rounded-2xl p-4 border border-indigo-500/20 text-[15px] text-indigo-100/90 tracking-wide">
                ज़रूर, मैं रेंट एग्रीमेंट (किरायेनामा) के कानूनी पहलुओं को समझने में आपकी मदद कर सकता हूँ।
              </div>
            </div>
          </div>
        </div>

        {/* Visual Asset */}
        <motion.div
          className="w-1/2 flex justify-center items-center"
          animate={{ y: [-15, 15, -15] }}
          transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
        >
          <div className="relative w-full max-w-[400px] aspect-square rounded-[32px] overflow-hidden border border-white/10 shadow-[0_0_100px_rgba(99,102,241,0.2)]">
            <Image
              src="/assets/legal_ai_assistant.png"
              alt="AI Legal Assistant Core"
              fill
              className="object-cover"
              priority
            />
          </div>
        </motion.div>
      </motion.div>

      {/* Slide 2: RAG & Citations */}
      <motion.div style={{ opacity: opacity2, y: y2, pointerEvents: 'none' }} className="absolute inset-0 p-12 flex items-center justify-between text-left">
        <div className="w-1/2 pr-8">
          <div className="inline-flex py-1 px-3 rounded text-sm bg-blue-500/20 text-blue-300 mb-6 font-medium">IPC & CrPC Aware</div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">
            Backed by True Citations.
          </h2>
          <p className="text-xl text-white/50 max-w-2xl font-light mb-8">
            Not just generative LLM text. Our RAG engine searches actual Indian statute databases to give you the precise sections.
          </p>
          <div className="w-full">
            <div className="bg-[#1a1d27]/60 backdrop-blur-lg rounded-[20px] p-6 border border-white/10 text-white/90 shadow-[0_20px_50px_rgba(0,0,0,0.5)] relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-1.5 h-full bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.8)]" />
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/0 via-blue-500/5 to-transparent group-hover:via-blue-500/10 transition-colors pointer-events-none" />
              <p className="font-semibold mb-4 text-blue-300 tracking-wide uppercase text-xs">Legal Context Found</p>
              <p className="text-[15px] font-light leading-relaxed">
                Under <span className="bg-yellow-500/20 text-yellow-300 px-1.5 py-0.5 rounded border border-yellow-500/30">Section 415 of the IPC (Indian Penal Code)</span>, whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property...
              </p>
            </div>
          </div>
        </div>

        {/* Visual Asset */}
        <motion.div
          className="w-1/2 flex justify-center items-center"
          animate={{ y: [-15, 15, -15] }}
          transition={{ repeat: Infinity, duration: 7, ease: "easeInOut" }}
        >
          <div className="relative w-full max-w-[400px] aspect-square rounded-[32px] overflow-hidden border border-white/10 shadow-[0_0_100px_rgba(59,130,246,0.2)]">
            <Image
              src="/assets/rag_legal_documents.png"
              alt="Digital Law Books Data Nodes"
              fill
              className="object-cover"
              priority
            />
          </div>
        </motion.div>
      </motion.div>

      {/* Slide 3: Instant Drafts & PDF Gen */}
      <motion.div style={{ opacity: opacity3, y: y3, pointerEvents: 'none' }} className="absolute inset-0 p-12 flex items-center justify-between text-left">
        <div className="w-1/2 pr-8">
          <div className="inline-flex py-1 px-3 rounded text-sm bg-pink-500/20 text-pink-300 mb-6 font-medium">Instant Drafts</div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">
            Ready-to-Print Documents.
          </h2>
          <p className="text-xl text-white/50 max-w-2xl font-light mb-8">
            From legal analysis directly into professionally formatted PDFs for FIRs, RTIs, and Complaints.
          </p>

          <button className="px-6 py-3 bg-pink-500 hover:bg-pink-600 transition-colors text-white rounded-xl font-medium shadow-lg shadow-pink-500/20 pointer-events-auto">
            Try Generating a Draft
          </button>
        </div>

        {/* Visual Asset */}
        <motion.div
          className="w-1/2 flex justify-center items-center"
          animate={{ y: [-15, 15, -15] }}
          transition={{ repeat: Infinity, duration: 5.5, ease: "easeInOut" }}
        >
          <div className="relative w-full max-w-[400px] aspect-square rounded-[32px] overflow-hidden border border-white/10 shadow-[0_0_100px_rgba(236,72,153,0.2)]">
            <Image
              src="/assets/instant_pdf_drafts.png"
              alt="Futuristic PDF Generation tablet"
              fill
              className="object-cover"
              priority
            />
          </div>
        </motion.div>
      </motion.div>

    </div>
  );
}
