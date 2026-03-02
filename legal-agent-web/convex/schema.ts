import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    name: v.optional(v.string()),
    email: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    state: v.optional(v.string()), // Used for scheme recommendations
    language: v.optional(v.string()), // Preferred language
  }).index("by_clerkId", ["clerkId"]),

  chats: defineTable({
    userId: v.id("users"),
    title: v.string(),
    createdAt: v.number(),
  }).index("by_userId", ["userId"]),

  messages: defineTable({
    chatId: v.id("chats"),
    role: v.union(v.literal("user"), v.literal("agent")),
    content: v.string(),
    contextUsed: v.optional(v.string()), // To show references
    createdAt: v.number(),
  }).index("by_chatId", ["chatId"]),

  documents: defineTable({
    userId: v.id("users"),
    title: v.string(),
    type: v.string(), // "FIR", "RTI", "Notice"
    url: v.string(), // URL to generated PDF if stored externally or in Convex File Storage
    createdAt: v.number(),
  }).index("by_userId", ["userId"]),
});
