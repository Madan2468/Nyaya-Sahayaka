"use client";

import { UserButton, useUser } from "@clerk/nextjs";
import { Scale, Plus, Settings } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useQuery, useMutation } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user } = useUser();
  const [isOpen, setIsOpen] = useState(true);

  // Sync clerk user to convex
  const storeUser = useMutation(api.users.storeUser);
  useEffect(() => {
    if (user) {
      storeUser({
        clerkId: user.id,
        name: user.fullName || "",
        email: user.primaryEmailAddress?.emailAddress || "",
        imageUrl: user.imageUrl || ""
      });
    }
  }, [user, storeUser]);

  const chats = useQuery(api.chats.getChatsForUser, user ? { clerkId: user.id } : "skip");

  return (
    <div className="flex bg-[#030305] text-white overflow-hidden h-screen fixed inset-0 font-light">

      {/* Background Ambient Glow */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-1/4 w-[1000px] h-[1000px] bg-indigo-900/10 rounded-full blur-[150px] mix-blend-screen opacity-50" />
        <div className="absolute bottom-0 left-1/4 w-[800px] h-[800px] bg-purple-900/10 rounded-full blur-[150px] mix-blend-screen opacity-50" />
      </div>

      {/* Floating Sidebar Navigation */}
      <AnimatePresence mode="wait">
        {isOpen && (
          <motion.aside
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="w-[320px] shrink-0 m-4 mr-0 rounded-[32px] border border-white/5 bg-[#0a0a0c]/80 backdrop-blur-2xl flex flex-col shadow-2xl relative z-20 overflow-hidden"
          >

            {/* App Title */}
            <div className="p-6 flex items-center gap-4 border-b border-white/[0.04] shrink-0">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-2xl shadow-[0_0_30px_rgba(99,102,241,0.3)]">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <span className="font-medium text-xl tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                Nyaya Sahayaka
              </span>
            </div>

            {/* New Chat Button */}
            <div className="p-5 shrink-0 z-10">
              <Button onClick={() => window.location.reload()} className="w-full bg-white/[0.03] hover:bg-white/[0.08] text-white/90 border border-white/5 hover:border-white/10 shadow-lg rounded-2xl flex items-center justify-start px-5 h-14 transition-all group overflow-hidden relative" variant="ghost">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/0 via-indigo-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                <div className="bg-white/5 p-1.5 rounded-lg mr-4 group-hover:bg-indigo-500 group-hover:text-white transition-colors duration-300">
                  <Plus className="w-4 h-4" />
                </div>
                <span className="font-medium tracking-wide text-[15px]">New Consultation</span>
              </Button>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto px-5 py-2 space-y-1 relative z-10 custom-scrollbar">
              <div className="text-[10px] font-bold text-white/30 mb-5 uppercase tracking-[0.2em] px-2">Recent Sessions</div>

              {chats?.map((chat) => (
                <div key={chat._id} className="px-5 py-3.5 rounded-2xl bg-transparent border border-transparent hover:border-white/5 hover:bg-white/[0.03] hover:shadow-xl hover:shadow-black/50 cursor-pointer transition-all text-[14px] text-white/50 hover:text-white/90 font-light tracking-wide line-clamp-1 group relative">
                  <span className="relative z-10 line-clamp-1 pr-4">{chat.title}</span>
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              ))}
              {chats?.length === 0 && (
                <div className="px-3 text-[13px] text-white/30 text-center mt-8 font-light italic">No robust history available</div>
              )}
            </div>

            {/* User Profile Footer */}
            <div className="p-6 border-t border-white/[0.04] flex items-center justify-between shrink-0 bg-black/20 relative z-20 backdrop-blur-xl">
              <div className="flex items-center gap-4">
                <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: "w-11 h-11 border-2 border-white/10 rounded-2xl transition-all hover:border-indigo-500" } }} />
                <div className="flex flex-col">
                  <span className="text-[15px] font-medium tracking-wide text-white/95">{user?.firstName || "Citizen"}</span>
                  <span className="text-[10px] text-indigo-400 font-medium uppercase tracking-[0.15em] mt-1">Free Tier</span>
                </div>
              </div>
              <Button variant="ghost" size="icon" className="h-10 w-10 bg-white/5 text-white/60 hover:text-white hover:bg-white/10 border border-white/5 rounded-full transition-all hover:rotate-90 duration-300">
                <Settings className="w-4 h-4" />
              </Button>
            </div>

          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative w-full h-screen bg-transparent z-10">
        {children}
      </main>
    </div>
  );
}
