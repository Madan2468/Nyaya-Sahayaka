import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const outfit = Outfit({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Nyaya Sahayaka | AI Legal Assistant",
  description: "Multilingual AI Legal & Government Scheme Assistance for Indian Citizens",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${outfit.className} min-h-screen bg-background antialiased selection:bg-indigo-500/30`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
