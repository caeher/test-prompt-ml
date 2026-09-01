import type { Metadata } from "next";
import "../src/index.css";

export const metadata: Metadata = {
  title: "Análisis de toxicidad — mBERT",
  description: "Clasificador multiclase en español salvadoreño",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
