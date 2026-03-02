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

export default function ChatPage() {
  const { user } = useUser();
  const [chatId, setChatId] = useState<Id<"chats"> | null>(null);
  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const createChat = useMutation(api.chats.createChat);
  const addMessage = useMutation(api.messages.addMessage);

  // Fetch messages if a chat exists
  const rawMessages = useQuery(api.messages.getMessagesForChat, chatId ? { chatId } : "skip") || [];
  const messages = useMemo(() => rawMessages, [rawMessages]);

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
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: messageText,
          language: "en",
          chat_history: [] // could map previous messages here
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
    <div className="flex flex-col h-full bg-transparent relative z-10 font-light text-white overflow-hidden">

      {/* Scrollable Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 md:px-12 pt-12 pb-32 custom-scrollbar" ref={scrollRef}>
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <motion.div
              key="empty-state"
              initial="hidden" animate="show" exit={{ opacity: 0, scale: 0.95 }}
              variants={containerVariants}
              className="flex flex-col items-center justify-center h-full text-center space-y-10 px-4 mt-20"
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
            <div className="space-y-8 max-w-4xl mx-auto w-full pb-10">
              {messages.map((msg, i) => (
                <motion.div
                  key={msg._id}
                  initial={{ opacity: 0, y: 20, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ type: "spring", damping: 25, stiffness: 200, delay: Math.min(i * 0.05, 1) }}
                  className={`flex gap-5 group ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-lg border ${msg.role === 'user' ? 'bg-[#151518] border-white/5' : 'bg-gradient-to-br from-indigo-500 to-purple-600 border-indigo-500/30'}`}>
                    {msg.role === 'user' ? <User className="w-5 h-5 text-white/70" /> : <Bot className="w-5 h-5 text-white" />}
                  </div>

                  <div className={`flex flex-col text-sm max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`p-6 rounded-[28px] shadow-2xl backdrop-blur-2xl transition-all duration-300 ${msg.role === 'user' ? 'bg-indigo-500/10 hover:bg-indigo-500/15 border border-indigo-500/20 text-white rounded-tr-sm' : 'bg-[#0f0f12]/80 hover:bg-[#121216]/90 border border-white-[0.05] text-white/90 rounded-tl-sm'}`}>
                      {msg.role === 'user' ? (
                        <div className="whitespace-pre-wrap text-[16px] tracking-wide leading-relaxed font-light">{msg.content}</div>
                      ) : (
                        <div className="markdown-prose">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ ...props }) => <p className="mb-5 last:mb-0 leading-[1.8] tracking-wide text-[15px] font-light text-white/85" {...props} />,
                              ul: ({ ...props }) => <ul className="list-disc ml-6 mb-5 space-y-3 marker:text-indigo-400 text-white/85 font-light" {...props} />,
                              ol: ({ ...props }) => <ol className="list-decimal ml-6 mb-5 space-y-3 marker:text-indigo-400 text-white/85 font-light" {...props} />,
                              li: ({ ...props }) => <li className="pl-2 line-height-[1.8] text-[15px]" {...props} />,
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
                      <details className="mt-3 text-xs text-white/40 bg-white/[0.02] hover:bg-white/[0.04] p-4 rounded-2xl cursor-pointer max-w-full overflow-hidden border border-white/[0.05] transition-colors duration-300">
                        <summary className="font-medium text-white/50 hover:text-white/80 transition-colors outline-none select-none">View Legal Strategy & RAG Context</summary>
                        <p className="mt-4 text-white/40 whitespace-pre-wrap leading-relaxed border-t border-white/5 pt-4 font-mono text-[11px] opacity-70">{msg.contextUsed}</p>
                      </details>
                    )}
                  </div>
                </motion.div>
              ))}

              {isGenerating && (
                <motion.div
                  initial={{ opacity: 0, y: 20, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ type: "spring", damping: 25, stiffness: 200 }}
                  className="flex gap-5 flex-row"
                >
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-[0_0_30px_rgba(99,102,241,0.5)]">
                    <Bot className="w-5 h-5 text-white animate-pulse" />
                  </div>
                  <div className="p-5 rounded-[28px] rounded-tl-sm bg-gradient-to-r from-[#0f0f12]/90 to-[#15151a]/90 border border-indigo-500/20 text-indigo-300 flex items-center gap-3 shadow-2xl backdrop-blur-2xl font-medium tracking-wide text-[15px] relative overflow-hidden">
                    <div className="absolute inset-0 bg-indigo-500/10 animate-pulse" />
                    <Loader2 className="w-5 h-5 animate-spin relative z-10" />
                    <span className="animate-pulse relative z-10">Mining IPC, CrPC, & Welfare Schematics...</span>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Floating Input Area */}
      <div className="absolute bottom-6 left-0 right-0 px-6 z-30 pointer-events-none">
        <div className="max-w-4xl mx-auto relative group pointer-events-auto">
          {/* Animated Glow behind input */}
          <div className="absolute -inset-2 bg-gradient-to-r from-indigo-500/30 via-purple-500/30 to-indigo-500/30 rounded-[32px] blur-2xl opacity-50 group-hover:opacity-100 group-focus-within:opacity-100 transition duration-1000" />

          <div className="relative flex items-end gap-3 bg-[#0a0a0c]/90 backdrop-blur-3xl border border-white/10 rounded-[28px] p-3 shadow-2xl transition-all focus-within:border-indigo-500/50 focus-within:bg-[#0a0a0c]">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Draft a notice, explore schemes, or ask a legal question..."
              className="border-0 focus-visible:ring-0 bg-transparent text-white placeholder:text-white/30 resize-none min-h-[52px] shadow-none h-14 text-[16px] tracking-wide font-light px-5"
            />
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim() || isGenerating}
              size="icon"
              className="h-14 w-14 shrink-0 rounded-[20px] bg-white hover:bg-gray-200 text-black transition-all shadow-[0_0_30px_rgba(255,255,255,0.15)] hover:shadow-[0_0_40px_rgba(255,255,255,0.3)] disabled:opacity-30 disabled:shadow-none hover:scale-105 active:scale-95"
            >
              {isGenerating ? <Loader2 className="w-6 h-6 animate-spin text-indigo-600" /> : <Send className="w-6 h-6 ml-1 text-black" />}
            </Button>
          </div>
          <p className="text-center text-[11px] text-white/30 mt-5 font-light tracking-wide uppercase">
            AI-generated legal assistance framework • Not formal legal advice
          </p>
        </div>
      </div>
    </div>
  );
}

function PromptCard({ icon, text, onClick, delay }: { icon?: React.ReactNode, text: string, onClick: () => void, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay, type: "spring", stiffness: 100 }}
      whileHover={{ y: -5, scale: 1.02, backgroundColor: "rgba(255,255,255,0.05)" }}
      onClick={onClick}
      className="flex items-center gap-4 p-5 rounded-[24px] bg-white/[0.02] border border-white/5 cursor-pointer transition-all group text-left backdrop-blur-md shadow-xl overflow-hidden relative"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/0 via-indigo-500/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
      <div className="w-12 h-12 rounded-[16px] bg-white/[0.03] flex items-center justify-center text-white/50 group-hover:text-white group-hover:bg-indigo-500 transition-colors duration-300 shrink-0 border border-white/5 relative z-10 shadow-inner">
        {icon || <Info className="w-5 h-5" />}
      </div>
      <p className="text-[15px] text-white/60 group-hover:text-white/95 transition-colors font-light leading-relaxed tracking-wide relative z-10 pr-2">{text}</p>
    </motion.div>
  );
}
