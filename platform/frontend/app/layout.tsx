// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Providers } from "./providers";
import { THEME_STORAGE_KEY } from "@/lib/themes";
import { LOCALE_STORAGE_KEY } from "@/lib/i18n";
import "./globals.css";
import "@/styles/pages.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "OctoRig",
  description: "Vulnerable lab platform for penetration testing and security research",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="nord" suppressHydrationWarning>
      <head>
        {/* FOUC prevention — apply stored theme before first paint */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var s=localStorage.getItem(${JSON.stringify(THEME_STORAGE_KEY)});if(s){var t=JSON.parse(s).state?.theme;if(t)document.documentElement.setAttribute("data-theme",t);}}catch(e){}`,
          }}
        />
        {/* Apply stored locale to <html lang> before first paint — translated text still loads client-side via IntlProvider */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var s=localStorage.getItem(${JSON.stringify(LOCALE_STORAGE_KEY)});if(s){var l=JSON.parse(s).state?.locale;if(l)document.documentElement.setAttribute("lang",l);}}catch(e){}`,
          }}
        />
      </head>
      <body className={`${inter.variable} ${mono.variable} font-sans flex flex-col h-screen overflow-hidden antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
