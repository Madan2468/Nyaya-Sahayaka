"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { useUser } from "@clerk/nextjs";
import { useState, useRef, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User, FileText, Loader2, Info, Scale } from "lucide-react";
import { Id } from "../../../convex/_generated/dataModel";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from "framer-motion";
import { Settings2, X, Mic, MicOff, Volume2, Phone, PhoneOff, Square, Shield, ArrowRight } from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";

export default function ChatPage() {
  const { user } = useUser();
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const chatIdStr = searchParams.get("id");
  const chatId = chatIdStr ? (chatIdStr as Id<"chats">) : null;
  const setChatId = (id: Id<"chats"> | null) => {
    if (id) router.push(`/chat?id=${id}`);
    else router.push("/chat");
  };

  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [callMode, setCallMode] = useState(false);
  const [playingMsgId, setPlayingMsgId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const callModeRef = useRef<boolean>(false);
  
  const [showProfile, setShowProfile] = useState(false);
  const [profile, setProfile] = useState({ state: "All", gender: "All", caste: "All", language: "en" });

  const langMap: Record<string, string> = { "en": "en-IN", "hi": "hi-IN", "bn": "bn-IN", "ta": "ta-IN" };

  const createChat = useMutation(api.chats.createChat);
  const addMessage = useMutation(api.messages.addMessage);

  // Fetch messages if a chat exists
  const rawMessages = useQuery(api.messages.getMessagesForChat, chatId ? { chatId } : "skip") || [];
  const messages = useMemo(() => rawMessages, [rawMessages]);

  const stopTTS = () => {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setPlayingMsgId(null);
  };

  const handleTTS = (text: string, msgId: string, onEndCallback?: () => void) => {
    if (!window.speechSynthesis) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel(); // Stop any pending speech
    setPlayingMsgId(msgId);
    const cleanText = text.replace(/#+\s/g, '').replace(/\*/g, '').replace(/- \[\s?\]/g, 'Step: ');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = langMap[profile.language] || "en-IN";
    utterance.onend = () => { 
      setPlayingMsgId(null);
      if (onEndCallback) onEndCallback(); 
    };
    window.speechSynthesis.speak(utterance);
  };

  const toggleListen = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.abort();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = langMap[profile.language] || "en-IN";
    recognition.interimResults = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + (prev ? " " : "") + transcript);
    };
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const callListen = () => {
    if (!callModeRef.current) return;
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = langMap[profile.language] || "en-IN";
    recognition.interimResults = false;
    
    // Barge-in and Auto Hangup support
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      if (transcript.trim() && callModeRef.current) {
        if (playingMsgId) stopTTS(); // Instantly barge in and stop the AI
        
        const lc = transcript.toLowerCase();
        if (lc.includes("goodbye") || lc.includes("bye") || lc.includes("cut the call") || lc.includes("thank you") || lc.includes("thanks") || lc.includes("stop") || lc.includes("done")) {
           handleSend(transcript);
           toggleCallMode(); // shut off
           return;
        }

        handleSend(transcript);
      }
    };
    recognition.onend = () => {
       // Only restart automatically if we are still active, but usually handleSend will trigger TTS. 
       // For a robust loop, we restart only after TTS is done.
       setIsListening(false);
    };
    try { recognition.start(); setIsListening(true); } catch(e){}
  };

  const toggleCallMode = () => {
    if (callMode) {
      setCallMode(false);
      callModeRef.current = false;
      stopTTS();
      if (recognitionRef.current) recognitionRef.current.abort();
      setIsListening(false);
    } else {
      setCallMode(true);
      callModeRef.current = true;
      // Greeting before listening
      const greeting = profile.language === "hi" ? "नमस्ते! मैं न्याय सहायक हूँ। मैं आपकी क्या मदद कर सकता हूँ?" : 
                       (profile.language === "bn" ? "নমস্কার! আমি ন্যায় সহায়ক। আমি আপনাকে কীভাবে সাহায্য করতে পারি?" : 
                       "Hello! I am Nyaya Sahayaka. How can I help you today?");
      handleTTS(greeting, "system_greeting", () => {
        if (callModeRef.current) callListen();
      });
    }
  };

  const handleSend = async (forcedInput?: string) => {
    const messageText = forcedInput || input;
    if (!messageText.trim() || !user) return;

    setInput("");
    setIsGenerating(true);

    try {
      let currentChatId = chatId;

      // 1. Create chat if it's the first message
      if (!currentChatId) {
        currentChatId = await createChat({ clerkId: user.id, title: messageText.substring(0, 40) });
        setChatId(currentChatId);
      }

      // 2. Save User Message immediately to Convex
      await addMessage({
        chatId: currentChatId,
        role: "user",
        content: messageText
      });

      // 3. Call FastAPI End-to-End
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: messageText,
          language: profile.language,
          state: profile.state !== "All" ? profile.state : undefined,
          gender: profile.gender !== "All" ? profile.gender : undefined,
          caste: profile.caste !== "All" ? profile.caste : undefined,
          is_voice_mode: callModeRef.current,
          chat_history: messages.map((m: any) => ({ role: m.role, content: m.content }))
        })
      });

      const data = await response.json();

      // 4. Save AI Output to Convex
      if (data.response) {
        await addMessage({
          chatId: currentChatId,
          role: "agent",
          content: data.response,
          contextUsed: data.context_used
        });
        
        // Loop back listening for call mode
        if (callModeRef.current) {
          handleTTS(data.response, currentChatId, () => {
             if (callModeRef.current) callListen();
          });
        }
      }
    } catch (e) {
      console.error("FastAPI or Convex error", e);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  // Framer Motion Variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, damping: 20, stiffness: 100 } }
  };

  return (
    <div className="flex flex-col h-screen bg-[#020202] relative overflow-hidden font-sans selection:bg-indigo-500/30 selection:text-white">
      {/* Insane Ambient Mesh Background */}
      <div className="fixed inset-0 z-0 pointer-events-none mix-blend-screen">
        <motion.div animate={{ rotate: 360, scale: [1, 1.3, 1] }} transition={{ duration: 25, repeat: Infinity, ease: "linear" }} className="absolute -top-[20%] -left-[10%] w-[70vw] h-[70vh] rounded-full bg-indigo-600/10 blur-[120px]" />
        <motion.div animate={{ rotate: -360, scale: [1, 1.4, 1] }} transition={{ duration: 35, repeat: Infinity, ease: "linear" }} className="absolute top-[40%] -right-[10%] w-[60vw] h-[80vh] rounded-full bg-purple-700/10 blur-[150px]" />
        <motion.div animate={{ y: [0, -100, 0], x: [0, 50, 0] }} transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }} className="absolute -bottom-[20%] left-[20%] w-[50vw] h-[50vh] rounded-full bg-cyan-700/10 blur-[120px]" />
        
        {/* Film grain / noise overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjQiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')] opacity-[0.15] mix-blend-overlay" />
      </div>

      <div className="relative z-10 flex flex-col h-full w-full">
      {/* Profile Settings Interactive Drawer */}
      <AnimatePresence>
        {showProfile && (
          <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-md text-left overflow-hidden">
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setShowProfile(false)}
              className="absolute inset-0 z-0 bg-transparent cursor-pointer" 
            />
            
            <motion.div 
              initial={{ x: "100%", opacity: 0 }} 
              animate={{ x: 0, opacity: 1 }} 
              exit={{ x: "100%", opacity: 0 }}
              transition={{ type: "spring", damping: 30, stiffness: 350 }}
              className="bg-[#0a0a0c]/90 border-l border-white/10 p-10 max-w-sm w-full shadow-[0_0_100px_rgba(0,0,0,1)] relative z-10 backdrop-blur-3xl flex flex-col h-full"
            >
              <button onClick={() => setShowProfile(false)} className="absolute top-8 right-8 text-white/40 hover:text-white transition-colors bg-white/5 p-2 rounded-full hover:bg-white/10"><X className="w-5 h-5"/></button>
              
              <div className="w-14 h-14 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6 border border-indigo-500/40 shadow-[inset_0_0_30px_rgba(99,102,241,0.2)]">
                <Settings2 className="w-7 h-7 text-indigo-400" />
              </div>
              <h3 className="text-3xl font-medium text-white mb-2 tracking-tight">Agent Context</h3>
              <p className="text-white/40 text-[13px] mb-10 leading-relaxed font-light">Set your demographic bounds to inject precise geolocation and case context into the RAG model pipeline.</p>
              
              <div className="space-y-8 flex-1">
                <div>
                  <label className="text-[11px] text-indigo-300/70 font-bold uppercase tracking-[0.15em] block mb-3">Residential State</label>
                  <div className="relative">
                    <select value={profile.state} onChange={e => setProfile({...profile, state: e.target.value})} className="w-full bg-black/40 border border-white/10 text-white rounded-2xl p-4 outline-none focus:border-indigo-500 transition-all cursor-pointer appearance-none group text-[15px] tracking-wide shadow-inner">
                      <option value="All">All States (Union)</option>
                      <option value="Andhra Pradesh">Andhra Pradesh</option>
                      <option value="Madhya Pradesh">Madhya Pradesh</option>
                      <option value="West Bengal">West Bengal</option>
                      <option value="Chhattisgarh">Chhattisgarh</option>
                      <option value="Karnataka">Karnataka</option>
                    </select>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-[11px] text-indigo-300/70 font-bold uppercase tracking-[0.15em] block mb-3">Gender</label>
                    <select value={profile.gender} onChange={e => setProfile({...profile, gender: e.target.value})} className="w-full bg-black/40 border border-white/10 text-white rounded-2xl p-4 outline-none focus:border-indigo-500 transition-all cursor-pointer appearance-none text-[15px] tracking-wide shadow-inner">
                      <option value="All">Any</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-indigo-300/70 font-bold uppercase tracking-[0.15em] block mb-3">Category</label>
                    <select value={profile.caste} onChange={e => setProfile({...profile, caste: e.target.value})} className="w-full bg-black/40 border border-white/10 text-white rounded-2xl p-4 outline-none focus:border-indigo-500 transition-all cursor-pointer appearance-none text-[15px] tracking-wide shadow-inner">
                      <option value="All">General</option>
                      <option value="SC">SC</option>
                      <option value="ST">ST</option>
                      <option value="OBC">OBC</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-8 border-t border-white/5 pb-10">
                <Button onClick={() => setShowProfile(false)} className="w-full h-14 shadow-[0_0_30px_rgba(99,102,241,0.3)] bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white rounded-2xl text-[16px] font-semibold border border-white/10 tracking-wide transition-all hover:scale-[1.02]">
                  Sync Engine Context
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Floating Language Picker Header */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex items-center bg-[#0a0a0c]/80 backdrop-blur-2xl border border-white/5 rounded-full px-6 py-2.5 z-40 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.8)]">
         <span className="text-white/30 text-[10px] font-bold uppercase tracking-[0.2em] mr-4">Voice Engine</span>
         <select value={profile.language} onChange={e => setProfile({...profile, language: e.target.value})} className="bg-transparent text-indigo-400 group hover:text-indigo-300 text-sm font-semibold outline-none cursor-pointer appearance-none text-center">
           <option value="en">English (Default)</option>
           <option value="hi">Hindi (हिंदी)</option>
           <option value="bn">Bengali (বাঙালি)</option>
           <option value="ta">Tamil (தமிழ்)</option>
         </select>
      </div>

      {/* Premium Call Mode Overlay */}
      {callMode && (
        <AnimatePresence>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/60 backdrop-blur-2xl">
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black opacity-60 pointer-events-none z-0" />
            
            {/* Live Audio Visualizer Particle Ring */}
            <div className="relative mb-16 flex items-center justify-center cursor-pointer group" onClick={toggleListen}>
              <div className="relative z-10 w-64 h-64 flex items-center justify-center">
                {Array.from({ length: 48 }).map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{
                      height: isListening 
                        ? [12, Math.random() * 60 + 20, 12] 
                        : (playingMsgId ? [15, Math.random() * 40 + 20, 15] : 12),
                      opacity: isListening ? [0.4, 1, 0.4] : 0.4
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: isListening ? 0.4 : (playingMsgId ? 0.6 : 2),
                      ease: "easeInOut",
                      delay: i * 0.03
                    }}
                    className={`absolute w-1 rounded-full origin-bottom ${isListening ? 'bg-cyan-400 shadow-[0_0_15px_cyan]' : (playingMsgId ? 'bg-purple-400 shadow-[0_0_15px_purple]' : 'bg-white/20')}`}
                    style={{ transformOrigin: "0 128px", rotate: `${i * (360/48)}deg`, top: 0, left: "50%" }}
                  />
                ))}
                
                {/* Core Center Microphone Glass */}
                <div className={`relative z-20 w-32 h-32 rounded-full flex items-center justify-center bg-black/60 backdrop-blur-3xl border border-white/10 transition-all duration-700 shadow-2xl ${isListening ? 'border-cyan-400/50 shadow-[0_0_80px_rgba(34,211,238,0.4)] bg-cyan-900/20' : (playingMsgId ? 'border-purple-500/50 shadow-[0_0_60px_rgba(168,85,247,0.3)]' : '')}`}>
                  <Mic className={`w-10 h-10 transition-all duration-500 ${isListening ? 'text-cyan-300 drop-shadow-[0_0_20px_rgba(34,211,238,0.9)] scale-110 animate-pulse' : (playingMsgId ? 'text-purple-300 scale-105' : 'text-white/40')}`} />
                </div>
              </div>
            </div>
            
            <motion.h2 animate={{ opacity: [0.7, 1, 0.7] }} transition={{ repeat: Infinity, duration: 2 }} className="text-4xl font-light text-white tracking-widest mb-4 z-10 drop-shadow-md">
              {isListening ? 'Listening...' : (playingMsgId ? 'Speaking...' : 'Processing...')}
            </motion.h2>
            <p className="text-white/40 max-w-sm text-center mb-16 z-10 text-lg font-light leading-relaxed">
              Have a natural conversation. Ask legal bounds or discuss your situation.
            </p>

            <button onClick={toggleCallMode} className="relative z-10 bg-red-500/10 hover:bg-red-500 text-white rounded-full p-6 border border-red-500/30 backdrop-blur-xl shadow-[0_0_40px_rgba(239,68,68,0.2)] hover:shadow-[0_0_60px_rgba(239,68,68,0.6)] transition-all transform hover:scale-110 group">
              <PhoneOff className="w-8 h-8 group-hover:rotate-12 transition-transform" />
            </button>
          </motion.div>
        </AnimatePresence>
      )}

      {/* Scrollable Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 md:px-12 pt-12 pb-32 custom-scrollbar relative" ref={scrollRef}>
        
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <motion.div
              key="empty-state"
              initial="hidden" animate="show" exit={{ opacity: 0, scale: 0.95 }}
              variants={containerVariants}
              className="flex flex-col items-center justify-center h-full text-center space-y-10 px-4 mt-20 relative z-10"
            >

              <motion.div variants={itemVariants} className="relative w-40 h-40 md:w-48 md:h-48 mb-8 mx-auto flex items-center justify-center" style={{ perspective: 1200 }}>
                {/* Massive Outer Glow */}
                <div className="absolute inset-[-40px] bg-indigo-500/20 blur-[70px] rounded-full group-hover:bg-indigo-500/30 transition-colors duration-1000" />

                {/* Organic Morphing Liquid Blur 1 */}
                <motion.div
                  animate={{
                    rotate: [0, 90, 180, 270, 360],
                    borderRadius: ["50%", "40% 60% 70% 30% / 40% 50% 60% 50%", "50%"],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
                  className="absolute inset-4 bg-gradient-to-tr from-indigo-600 via-purple-500 to-transparent opacity-60 mix-blend-screen blur-[8px]"
                />

                {/* Organic Morphing Liquid Blur 2 */}
                <motion.div
                  animate={{
                    rotate: [360, 270, 180, 90, 0],
                    borderRadius: ["50%", "60% 40% 30% 70% / 60% 30% 70% 40%", "50%"],
                    scale: [1, 1.2, 1]
                  }}
                  transition={{ repeat: Infinity, duration: 12, ease: "linear" }}
                  className="absolute inset-4 bg-gradient-to-bl from-blue-400 via-indigo-500 to-transparent opacity-50 mix-blend-screen blur-[6px]"
                />

                {/* Counter-rotating 3D Tech Ring 1 */}
                <motion.div
                  animate={{ rotateZ: 360, rotateX: [60, 75, 60], rotateY: [30, 45, 30] }}
                  transition={{ repeat: Infinity, duration: 15, ease: "linear" }}
                  className="absolute inset-0 rounded-full border-[2px] border-indigo-500/20 border-t-indigo-400 border-b-transparent shadow-[inset_0_0_20px_rgba(99,102,241,0.2)]"
                  style={{ transformStyle: "preserve-3d" }}
                />

                {/* Counter-rotating 3D Tech Ring 2 */}
                <motion.div
                  animate={{ rotateZ: -360, rotateX: [40, 20, 40], rotateY: [-45, -20, -45] }}
                  transition={{ repeat: Infinity, duration: 20, ease: "linear" }}
                  className="absolute inset-[-15px] rounded-full border-[2px] border-purple-500/20 border-l-purple-400 border-r-transparent shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                  style={{ transformStyle: "preserve-3d" }}
                />

                {/* Core Floating Plate */}
                <motion.div
                  animate={{ y: [-5, 5, -5] }}
                  transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                  className="relative z-10 w-20 h-20 rounded-full bg-[#0a0a0c]/80 backdrop-blur-3xl border border-white/20 shadow-[0_0_40px_rgba(0,0,0,0.8)] flex items-center justify-center"
                >
                  <Scale className="w-8 h-8 text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
                </motion.div>
              </motion.div>

              <motion.div variants={itemVariants} className="space-y-4">
                <h2 className="text-4xl md:text-5xl font-medium tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
                  How can I guide you today?
                </h2>
                <p className="text-lg text-white/40 max-w-lg mx-auto font-light">
                  Ask legal questions, request document drafts, or explore government schemes in your native language.
                </p>
              </motion.div>

              <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl w-full pt-8">
                <PromptCard onClick={() => handleSend("Draft a legal notice for non-payment of rent")} icon={<FileText />} text="Draft a legal notice for non-payment of rent" delay={0.1} />
                <PromptCard onClick={() => handleSend("What is the KALIA scheme in Odisha?")} icon={<Info />} text="What is the KALIA scheme in Odisha?" delay={0.2} />
                <PromptCard onClick={() => handleSend("Mera landlord security deposit return nahi kar raha")} text="Mera landlord security deposit return nahi kar raha" delay={0.3} />
                <PromptCard onClick={() => handleSend("How to file FIR for domestic violence?")} text="How to file FIR for domestic violence?" delay={0.4} />
              </motion.div>
            </motion.div>
          ) : (
            <div className="space-y-0 max-w-4xl mx-auto w-full pb-10 relative">
              {messages.map((msg, i) => (
                <motion.div
                  key={msg._id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ damping: 25, stiffness: 200 }}
                  className="flex gap-6 relative group pt-6 pb-6"
                >
                  {/* Timeline Thread Line */}
                  {i !== messages.length - 1 && (
                    <div className="absolute left-[19px] top-[64px] bottom-[-24px] w-[2px] bg-white/5 group-hover:bg-indigo-500/20 transition-colors z-0" />
                  )}

                  <div className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-[0_4px_20px_rgba(0,0,0,0.5)] border ${msg.role === 'user' ? 'bg-gradient-to-br from-[#1a1a1f] to-[#111113] border-white/[0.15] shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]' : 'bg-gradient-to-br from-indigo-500 to-purple-600 border-indigo-400/50 shadow-[inset_0_1px_0_rgba(255,255,255,0.4)] ring-4 ring-[#0a0a0c]'}`}>
                    {msg.role === 'user' ? <User className="w-5 h-5 text-white/70" /> : <Bot className="w-5 h-5 text-white" />}
                  </div>

                  <div className={`flex flex-col text-sm w-full overflow-hidden`}>
                    <div className="text-white/40 text-xs tracking-widest uppercase mb-3 font-semibold translate-x-1">
                      {msg.role === 'user' ? (user?.firstName || "Citizen") : "Nyaya Sahayaka AI"}
                    </div>
                    <div className="relative transition-all duration-500">
                      {msg.role !== 'user' && (
                        <button onClick={() => playingMsgId === msg._id ? stopTTS() : handleTTS(msg.content, msg._id)} className={`absolute top-4 right-4 transition-colors p-2 rounded-full ${playingMsgId === msg._id ? 'text-red-400 bg-red-400/10 hover:bg-red-400/20' : 'text-white/30 hover:text-white hover:bg-white/5'}`} title={playingMsgId === msg._id ? "Stop Reading" : "Read Aloud"}>
                          {playingMsgId === msg._id ? <Square className="w-4 h-4 fill-current" /> : <Volume2 className="w-4 h-4" />}
                        </button>
                      )}
                      {msg.role === 'user' ? (
                        <div className="whitespace-pre-wrap text-[16px] tracking-wide leading-relaxed font-light">{msg.content}</div>
                      ) : (
                        <div className="markdown-prose">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ ...props }) => <p className="mb-5 last:mb-0 leading-[1.8] tracking-wide text-[15px] font-light text-white/95" {...props} />,
                              ul: ({ ...props }) => <ul className="list-disc ml-6 mb-5 space-y-3 marker:text-indigo-400 text-white/95 font-light" {...props} />,
                              ol: ({ ...props }) => <ol className="list-decimal ml-6 mb-5 space-y-3 marker:text-indigo-400 text-white/95 font-light" {...props} />,
                              li: ({ className, children, ...props }: any) => {
                                if (className === 'task-list-item') {
                                  return (
                                    <li className="flex items-start gap-4 my-3 text-white/90 bg-white/[0.02] hover:bg-white/[0.04] p-4 rounded-2xl transition-all border border-white/5 shadow-sm" {...props}>
                                      {children}
                                    </li>
                                  );
                                }
                                return <li className="pl-2 leading-[1.8] text-[15px]" {...props}>{children}</li>
                              },
                              input: ({ type, checked, ...props }: any) => {
                                if (type === 'checkbox') {
                                  return (
                                    <div className="relative flex items-center justify-center shrink-0 mt-0.5">
                                      <input type="checkbox" defaultChecked={checked} className="peer w-[22px] h-[22px] appearance-none border-2 border-white/20 rounded-[8px] bg-black/40 checked:bg-indigo-500 checked:border-indigo-500 transition-all cursor-pointer shadow-inner" {...props} />
                                      <div className="absolute inset-0 flex items-center justify-center text-white pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity">
                                        <svg width="12" height="10" viewBox="0 0 12 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1 5L4.5 8.5L11 1.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                                      </div>
                                    </div>
                                  );
                                }
                                return <input type={type} defaultChecked={checked} {...props} />
                              },
                              strong: ({ ...props }) => <strong className="font-semibold text-white tracking-wide" {...props} />,
                              em: ({ ...props }) => <em className="text-white/60 italic font-light" {...props} />,
                              h3: ({ ...props }) => <h3 className="text-xl font-medium text-white mt-10 mb-4 tracking-tight" {...props} />,
                              h4: ({ ...props }) => <h4 className="text-lg font-medium text-indigo-300 mt-8 mb-4 tracking-tight" {...props} />,
                              a: ({ ...props }) => <a className="text-indigo-400 hover:text-indigo-300 underline underline-offset-4 decoration-indigo-400/30 transition-colors" {...props} />
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                    {msg.contextUsed && (
                      <details className="mt-4 text-xs text-white/40 bg-white/[0.02] hover:bg-white/[0.04] rounded-2xl cursor-pointer max-w-full overflow-hidden border border-white/[0.05] transition-colors duration-300">
                        <summary className="font-medium text-white/60 hover:text-white/90 transition-colors outline-none select-none p-4 flex items-center gap-2">
                          <Shield className="w-4 h-4 text-indigo-400" />
                          View Legal Strategy & RAG Context
                        </summary>
                        <p className="px-6 pb-6 pt-2 text-white/40 whitespace-pre-wrap leading-relaxed font-mono text-[11px] opacity-70 bg-black/20">{msg.contextUsed}</p>
                      </details>
                    )}
                  </div>
                </motion.div>
              ))}

              {isGenerating && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  className="flex gap-6 relative group pt-6"
                >
                  <div className="absolute left-[19px] top-[-24px] bottom-[20px] w-[2px] bg-white/5 z-0" />
                  <div className="relative z-10 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 border border-indigo-500/30 flex items-center justify-center shrink-0 shadow-lg ring-4 ring-[#0a0a0c]">
                    <Bot className="w-5 h-5 text-white animate-pulse" />
                  </div>
                  <div className="flex flex-col text-sm w-full">
                    <div className="text-white/40 text-xs tracking-widest uppercase mb-3 font-semibold translate-x-1 animate-pulse">
                      Mining Statutes...
                    </div>
                    <div className="p-4 w-fit rounded-2xl bg-[#111116] border border-indigo-500/20 text-indigo-300 flex items-center gap-3 font-medium tracking-wide text-[14px]">
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                      Cross-referencing IPC, CrPC, & Welfare Schematics...
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </AnimatePresence>
      </div>

      <div className="p-4 md:p-8 shrink-0 bg-gradient-to-t from-[rgba(3,3,5,0.9)] via-[rgba(3,3,5,0.8)] to-transparent relative z-30 pt-20 backdrop-blur-[2px]">
        <div className="max-w-3xl mx-auto flex flex-col items-center">
          {/* Futuristic Floating Island Input Area */}
          <div className={`w-full bg-gradient-to-b from-[#0a0a0c]/90 to-[#111116]/90 backdrop-blur-3xl border border-white/10 rounded-[32px] p-2 relative group transition-all duration-500 shadow-[0_30px_60px_rgba(0,0,0,0.6),inset_0_1px_0_rgba(255,255,255,0.05)] focus-within:border-indigo-400/50 focus-within:shadow-[0_30px_80px_rgba(0,0,0,0.6),inset_0_1px_0_rgba(255,255,255,0.1),0_0_30px_rgba(99,102,241,0.2)] flex ${input.split('\n').length > 1 ? 'items-end' : 'items-center'}`}>
            <textarea
              rows={Math.min(input.split('\n').length, 5)}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a legal question..."
              className="border-0 focus-visible:ring-0 bg-transparent text-white placeholder:text-white/30 resize-none shadow-none min-h-[56px] py-4 text-[15px] tracking-wide font-light px-6 w-full outline-none custom-scrollbar"
            />
            <div className="flex items-center gap-1.5 pr-2 pl-2 pb-2 h-full shrink-0">
              <button
                onClick={toggleCallMode}
                title="Hands-free Call Mode"
                className="p-3.5 rounded-full transition-all md:block hover:text-white bg-indigo-500/10 hover:bg-indigo-500/25 text-indigo-400 group-focus-within:opacity-100"
              >
                <Phone className="w-[18px] h-[18px]" />
              </button>
              <button
                onClick={toggleListen}
                title="Dictate Message"
                className={`p-3.5 rounded-full transition-all ${isListening && !callMode ? 'bg-red-500/20 text-red-400 animate-pulse' : 'text-white/40 hover:text-white hover:bg-white/10'}`}
              >
                {isListening && !callMode ? <Mic className="w-[18px] h-[18px] drop-shadow-[0_0_10px_rgba(239,68,68,0.8)]" /> : <MicOff className="w-[18px] h-[18px]" />}
              </button>
              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || isGenerating}
                className="ml-1 h-12 w-12 rounded-full bg-white text-black hover:bg-indigo-100 transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:shadow-[0_0_30px_rgba(255,255,255,0.4)] disabled:opacity-30 disabled:shadow-none p-0 flex items-center justify-center shrink-0"
              >
                <ArrowRight className="w-5 h-5 text-black" />
              </Button>
            </div>
          </div>
          <p className="text-center text-[11px] text-white/30 mt-4 font-light tracking-wider uppercase">
            AI-generated legal framework • Not formal advice • <button onClick={() => setShowProfile(true)} className="hover:text-white underline underline-offset-4 decoration-white/20 transition-colors">Set Profile Options</button>
          </p>
        </div>
      </div>
      
      </div> {/* <-- CLosing tag for relative z-10 wrapper */}
    </div>
  );
}

function PromptCard({ icon, text, onClick, delay }: { icon?: React.ReactNode, text: string, onClick: () => void, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay, type: "spring", stiffness: 100 }}
      whileHover={{ y: -5, scale: 1.02, borderColor: "rgba(99,102,241,0.3)" }}
      onClick={onClick}
      className="flex items-center gap-4 p-5 rounded-[24px] bg-white/[0.02] border border-white/5 cursor-pointer transition-all group text-left backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.3)] overflow-hidden relative"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-indigo-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent transition-opacity duration-500" />
      <div className="w-12 h-12 rounded-[16px] bg-white/[0.03] flex items-center justify-center text-white/50 group-hover:text-white group-hover:bg-indigo-500 transition-colors duration-300 shrink-0 border border-white/5 relative z-10 shadow-inner">
        {icon || <Info className="w-5 h-5" />}
      </div>
      <p className="text-[15px] text-white/60 group-hover:text-white/95 transition-colors font-light leading-relaxed tracking-wide relative z-10 pr-2">{text}</p>
    </motion.div>
  );
}
