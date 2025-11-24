import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/useAuth";

export const metadata: Metadata = {
  title: "StudyQuest - Developer Dashboard",
  description: "Monochrome terminal-style learning dashboard",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Preload JetBrains Mono font for performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        {/* Preload hint for faster font loading */}
        <link
          rel="preload"
          href="https://fonts.gstatic.com/s/jetbrainsmono/v13/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOVkWM.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
      </head>
      <body className="font-mono antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
