"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

interface AgentState {
  plan?: string;
  post?: string;
  step?: string;
}

export default function Page() {
  const { state } = useCoAgent<AgentState>({
    name: "post_generator",
    initialState: { plan: "", post: "", step: "idle" },
  });

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">Post Generator</h1>
          <p className="text-slate-300 text-lg mb-8">
            Powered by Deep Agents + CopilotKit
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-xl overflow-hidden h-[600px]">
                <CopilotChat
                  labels={{
                    title: "Post Generator",
                    initial:
                      'Tell me a topic for a blog post (e.g., "Write a blog post about Deep Agents with CopilotKit")',
                  }}
                />
              </div>
            </div>

            {/* Live Post Preview */}
            <div className="lg:col-span-1">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 h-[600px] overflow-y-auto">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Live Preview
                </h3>
                {state?.step && (
                  <div className="mb-4 text-sm text-cyan-300">
                    Status: <span className="font-mono">{state.step}</span>
                  </div>
                )}
                {state?.plan && (
                  <div className="text-slate-300 mb-4">
                    <h4 className="font-semibold text-white mb-2">Plan</h4>
                    <pre className="text-xs whitespace-pre-wrap font-mono bg-slate-900 p-3 rounded border border-slate-700">
                      {state.plan}
                    </pre>
                  </div>
                )}
                {state?.post ? (
                  <div className="text-slate-300 space-y-2">
                    <h4 className="font-semibold text-white mb-2">Post</h4>
                    <pre className="text-xs whitespace-pre-wrap font-mono bg-slate-900 p-3 rounded border border-slate-700">
                      {state.post}
                    </pre>
                  </div>
                ) : (
                  <p className="text-slate-400 italic">
                    Post content will appear here as the agent generates it...
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
