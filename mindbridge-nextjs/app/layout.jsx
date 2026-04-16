import "./globals.css";

export const metadata = {
  title: "MindBridge AI — Mental Health Risk Prediction",
  description: "Empathy-First AI that interviews, listens, and predicts mental health risk using Decision Tree Classifier.",
  keywords: "mental health, AI, empathy map, depression screening, anxiety assessment",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin=""/>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap" rel="stylesheet"/>
      </head>
      <body style={{ margin:0, padding:0, background:"#0d0f1a" }}>
        {children}
      </body>
    </html>
  );
}
