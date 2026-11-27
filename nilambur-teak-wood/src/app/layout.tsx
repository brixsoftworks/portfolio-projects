import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://nilamburteakwood.com"),
  title: "Aiswarya Industries | Dealers in Wooden Furniture & Interior Designing | Nilambur",
  description:
    "Aiswarya Industries, Nilambur — Dealers in handcrafted wooden furniture, custom solid teak living sets, modular kitchens, bedroom suites, wooden wardrobes, and turnkey architectural interior designing. Contact: Janardhanan: +91 9447 631 731, Jithesh: +91 9656 663 063.",
  keywords: [
    "Aiswarya Industries",
    "Aiswarya Industries Nilambur",
    "Wooden Furniture Nilambur",
    "Interior Designing Kerala",
    "Nilambur Teak Furniture",
    "Custom Wooden Wardrobes",
    "Solid Wood Modular Kitchens",
    "Living Room Wooden Furniture",
    "Janardhanan Aiswarya",
    "Jithesh Aiswarya",
  ],
  openGraph: {
    title: "Aiswarya Industries | Dealers in Wooden Furniture & Interior Designing",
    description:
      "Handcrafted luxury wooden furniture and bespoke architectural interior designing from Mannuppadam, Eranhimangad P.O., Nilambur, Kerala.",
    url: "https://nilamburteakwood.com",
    siteName: "Aiswarya Industries",
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full w-full bg-[#0c0a09] m-0 p-0 overflow-hidden">
      <body className="h-full w-full bg-[#0c0a09] text-[#fdfbf7] m-0 p-0 overflow-hidden antialiased">
        {children}
      </body>
    </html>
  );
}
