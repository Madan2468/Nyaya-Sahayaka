"use client";

import { Button } from "@/components/ui/button";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { ArrowRight, Scale, Shield, FileText, Globe } from "lucide-react";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { LaptopScroll, ScrollContentBlocks } from "@/components/ui/laptop-scroll";

export default function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Keep these parallax variables as they might be used by the absolute bottom element (CTA)
  const opacity4 = useTransform(scrollYProgress, [0.55, 0.65], [0, 1]);
  const y4 = useTransform(scrollYProgress, [0.55, 0.65], [100, 0]);

  return (
    <div ref={containerRef} className="bg-[#030303] text-white selection:bg-indigo-500/30 font-light relative h-[400vh]">

      {/* Fixed Background Elements */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden flex items-center justify-center">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute w-[800px] h-[800px] bg-indigo-600/20 blur-[150px] rounded-full mix-blend-screen"
        />
        <motion.div
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute -top-1/4 -right-1/4 w-[600px] h-[600px] bg-purple-600/20 blur-[120px] rounded-full mix-blend-screen"
        />
      </div>

      {/* Fixed Sticky Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between p-6 max-w-7xl mx-auto backdrop-blur-md bg-[#030303]/50 border-b border-white/5">
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="bg-gradient-to-tr from-indigo-500 to-purple-600 p-2 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.2)]">
            <Scale className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-medium tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
            Nyaya Sahayaka
          </span>
        </div>
        <div className="flex items-center gap-4">
          <SignedOut>
            <SignInButton mode="modal">
              <Button variant="ghost" className="hover:bg-white/10 rounded-full text-white/70 font-light tracking-wide">
                Sign In
              </Button>
            </SignInButton>
            <SignInButton mode="modal">
              <Button className="rounded-full bg-white text-black hover:bg-neutral-200 font-medium tracking-wide shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-all">
                Get Started
              </Button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/chat">
              <Button className="rounded-full bg-white text-black hover:bg-neutral-200 font-medium tracking-wide shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-all mr-2">
                Open AI Assistant
              </Button>
            </Link>
            <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: "w-10 h-10 border border-white/10 rounded-xl" } }} />
          </SignedIn>
        </div>
      </nav>

      {/* --- SCROLLING CONTENT SECTIONS --- */}

      <LaptopScroll>
        {/* We use the same scroll tracking inside to animate the laptop screen content */}
        <ScrollContentBlocks scrollYProgress={scrollYProgress} />
      </LaptopScroll>

      {/* 4. Final CTA & 3D Features (Becomes interactive when reached) */}
      <motion.div style={{ opacity: opacity4, y: y4 }} className="relative flex flex-col items-center justify-center z-20 px-6 pt-32 pb-20 overflow-hidden pointer-events-auto bg-[#030303]">
        {/* Adds a gradient fade from the laptop scroll area to the solid bottom area */}
        <div className="absolute top-0 left-0 w-full h-40 bg-gradient-to-b from-transparent to-[#030303] pointer-events-none" />

        <div className="text-center mb-16 max-w-3xl relative z-10">
          <h2 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8">
            Meet <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">Nyaya Sahayaka</span>
          </h2>
          <div className="flex justify-center gap-4 mb-16">
            <SignedIn>
              <Link href="/chat">
                <Button size="lg" className="rounded-2xl bg-white text-black hover:bg-neutral-200 hover:scale-105 transition-all text-lg px-8 py-7 shadow-[0_0_40px_rgba(255,255,255,0.2)]">
                  Start Consultation <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
            </SignedIn>
            <SignedOut>
              <SignInButton mode="modal">
                <Button size="lg" className="rounded-2xl bg-white text-black hover:bg-neutral-200 hover:scale-105 transition-all text-lg px-8 py-7 shadow-[0_0_40px_rgba(255,255,255,0.2)]">
                  Talk to AI Assistant <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </SignInButton>
            </SignedOut>
          </div>
        </div>

        {/* 3D Glassmorphism Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full relative z-10">
          <FeatureCard
            icon={<Shield className="w-8 h-8 text-indigo-400" />}
            title="IPC & CrPC Aware"
            desc="Backed by a powerful RAG engine that cites exact sections so you understand your true legal standing."
          />
          <FeatureCard
            icon={<Globe className="w-8 h-8 text-purple-400" />}
            title="Multilingual Support"
            desc="Speak naturally in Hindi, Bengali, Tamil, Telugu, Odia or Marathi. The AI translates everything flawlessly."
          />
          <FeatureCard
            icon={<FileText className="w-8 h-8 text-pink-400" />}
            title="Instant Legal Drafts"
            desc="Generate ready-to-print PDFs for FIRs, RTIs, and Consumer Complaints in seconds."
          />
        </div>

        <div className="mt-24 text-center text-white/20 text-sm tracking-widest uppercase pb-10 relative z-10">
          Powered by Gemini AI • FAISS • React
        </div>

      </motion.div>

    </div>
  );
}

// Interactive 3D Card Component
function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <motion.div
      whileHover={{ y: -10, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className="bg-[#111113]/60 border border-white/5 p-8 rounded-[32px] backdrop-blur-xl hover:border-white/10 hover:bg-[#151518]/80 transition-colors text-left group shadow-2xl relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />
      <div className="bg-white/5 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-inner border border-white/5">
        {icon}
      </div>
      <h3 className="text-xl font-medium mb-4 tracking-wide text-white/90">{title}</h3>
      <p className="text-white/40 leading-relaxed font-light text-[15px]">{desc}</p>
    </motion.div>
  );
}
