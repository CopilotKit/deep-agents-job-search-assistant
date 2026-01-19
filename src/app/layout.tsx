import type { Metadata } from "next";

import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata: Metadata = {
  title: "Post Generator | Deep Agents with CopilotKit",
  description: "Demo showing how to integrate CopilotKit with Deep Agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={"antialiased"}>
        <CopilotKit runtimeUrl="/api/copilotkit" agent="job_application_assistant">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
