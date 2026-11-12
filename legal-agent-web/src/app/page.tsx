"use client";

import { Button } from "@/components/ui/button";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { ArrowRight, Scale, Shield, Globe, Sparkles } from "lucide-react";
import Link from "next/link";
import { motion, useScroll, useTransform, useMotionTemplate, useMotionValue } from "framer-motion";
import { useRef, MouseEvent, useEffect } from "react";
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

      {/* Noise Texture Overlay */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03] mix-blend-screen" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.85%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")', backgroundRepeat: 'repeat' }} />

      {/* Grid Pattern Overlay */}
      <div className="fixed inset-0 z-0 pointer-events-none bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

      {/* RAG Network Canvas Connection visualizer */}
      <NetworkCanvas />

      {/* Fixed Background Intense Orbs */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden flex items-center justify-center">
        <motion.div
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.15, 0.35, 0.15],
            rotate: [0, 90, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute w-[900px] h-[900px] bg-indigo-600/30 blur-[150px] rounded-full mix-blend-screen"
        />
        <motion.div
          animate={{
            scale: [1, 1.8, 1],
            opacity: [0.1, 0.3, 0.1],
            rotate: [0, -90, 0]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute -top-1/4 -right-1/4 w-[700px] h-[700px] bg-purple-600/30 blur-[130px] rounded-full mix-blend-screen"
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
          <div className="flex justify-center gap-4 mb-16 relative">
            {/* Backdrop intense glow for buttons */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[100px] bg-indigo-500/40 blur-[80px] rounded-full pointer-events-none" />
            
            <SignedIn>
              <Link href="/chat">
                <motion.div animate={{ boxShadow: ["0 0 30px rgba(255,255,255,0.2)", "0 0 60px rgba(255,255,255,0.5)", "0 0 30px rgba(255,255,255,0.2)"] }} transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }} className="rounded-2xl">
                  <Button size="lg" className="rounded-2xl relative overflow-hidden bg-white text-black hover:bg-neutral-200 hover:scale-105 transition-all text-lg px-10 py-8 shadow-[0_0_50px_rgba(255,255,255,0.3)] group z-10 border border-white/20">
                    <span className="relative z-10 flex items-center font-bold tracking-tight">
                      Start Consultation <ArrowRight className="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
                    </span>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 z-0" />
                  </Button>
                </motion.div>
              </Link>
            </SignedIn>
            <SignedOut>
              <SignInButton mode="modal">
                <motion.div animate={{ boxShadow: ["0 0 30px rgba(255,255,255,0.2)", "0 0 60px rgba(255,255,255,0.5)", "0 0 30px rgba(255,255,255,0.2)"] }} transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }} className="rounded-2xl">
                  <Button size="lg" className="rounded-2xl relative overflow-hidden bg-white text-black hover:bg-neutral-200 hover:scale-105 transition-all text-lg px-10 py-8 shadow-[0_0_50px_rgba(255,255,255,0.3)] group z-10 border border-white/20">
                    <span className="relative z-10 flex items-center font-bold tracking-tight">
                      Talk to AI Assistant <ArrowRight className="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
                    </span>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 z-0" />
                  </Button>
                </motion.div>
              </SignInButton>
            </SignedOut>
          </div>
        </div>

        {/* Infinite Capability Marquee */}
        <InfiniteMarquee />

        {/* 3D Glassmorphism Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full relative z-10 mt-16">
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
            icon={<Sparkles className="w-8 h-8 text-emerald-400" />}
            title="Government Scheme Finder"
            desc="Discover welfare schemes tailored to your profile. Get eligibility details and application steps in your local language."
          />
        </div>

        <div className="mt-24 text-center text-white/20 text-sm tracking-widest uppercase pb-10 relative z-10">
          Powered by Gemini AI • FAISS • React
        </div>

      </motion.div>

    </div>
  );
}

// Interactive 3D Card Component with Spotlight
function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      whileHover={{ y: -12, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className="group relative bg-[#111113]/80 border border-white/5 p-8 rounded-[32px] backdrop-blur-2xl transition-colors text-left shadow-[0_0_40px_rgba(0,0,0,0.5)] overflow-hidden"
    >
      {/* Animated soft gradient follow mouse */}
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-[31px] opacity-0 transition duration-500 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              400px circle at ${mouseX}px ${mouseY}px,
              rgba(34, 211, 238, 0.15) 0%,
              rgba(99, 102, 241, 0.15) 30%,
              transparent 80%
            )
          `,
        }}
      />
      {/* Glowing border trace follow mouse */}
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-[31px] opacity-0 transition duration-500 group-hover:opacity-100 border border-indigo-500/50"
        style={{
          WebkitMaskImage: useMotionTemplate`
            radial-gradient(
              200px circle at ${mouseX}px ${mouseY}px,
              black,
              transparent
            )
          `,
        }}
      />

      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.04] to-transparent pointer-events-none" />
      
      <div className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 bg-white/[0.03] shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10 group-hover:border-indigo-500/50 group-hover:bg-indigo-500/10 transition-all duration-500 group-hover:scale-110">
        {icon}
      </div>
      <h3 className="relative z-10 text-xl font-bold mb-4 tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-white to-white/70 group-hover:from-white group-hover:to-indigo-200 transition-colors">
        {title}
      </h3>
      <p className="relative z-10 text-white/50 leading-relaxed font-light text-[15px] group-hover:text-white/70 transition-colors">
        {desc}
      </p>
    </motion.div>
  );
}

// RAG AI Node Canvas Visualizer
function NetworkCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    const nodes = Array.from({ length: 60 }).map(() => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      radius: Math.random() * 1.5 + 0.5
    }));

    let animationFrame: number;
    const render = () => {
      ctx.clearRect(0, 0, width, height);

      nodes.forEach(node => {
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(99, 102, 241, 0.5)";
        ctx.fill();
      });

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 180) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${0.15 * (1 - dist / 180)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      animationFrame = requestAnimationFrame(render);
    };

    render();

    const handleResize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none mix-blend-screen opacity-60" />;
}

// Cinematic Infinite Scrolling Marquee
function InfiniteMarquee() {
  const items = [
    "RTI Drafting", "FIR Filing", "Consumer Court", "Rental Agreements",
    "Divorce Consultation", "Cybercrime Reporting", "Property Law", "Labour Rights",
    "RTI Drafting", "FIR Filing", "Consumer Court", "Rental Agreements",
    "Divorce Consultation", "Cybercrime Reporting", "Property Law", "Labour Rights"
  ];

  return (
    <div className="w-full relative z-10 flex overflow-hidden border-y border-white/5 bg-[#0a0a0c]/80 backdrop-blur-md py-4">
      <div className="absolute top-0 left-0 w-32 h-full bg-gradient-to-r from-[#030303] to-transparent z-10" />
      <div className="absolute top-0 right-0 w-32 h-full bg-gradient-to-l from-[#030303] to-transparent z-10" />
      
      <motion.div
        className="flex whitespace-nowrap"
        animate={{ x: ["0%", "-50%"] }}
        transition={{ ease: "linear", duration: 30, repeat: Infinity }}
      >
        {items.map((item, i) => (
          <div key={i} className="flex items-center mx-6">
            <span className="text-white/40 tracking-widest uppercase text-sm font-medium">{item}</span>
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500/50 mx-6 shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
          </div>
        ))}
      </motion.div>
    </div>
  );
}
