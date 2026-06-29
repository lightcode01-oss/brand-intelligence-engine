'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Terminal, Code2, Server } from 'lucide-react';

export default function ApiDocsPage() {
  const [activeTab, setActiveTab] = useState<'curl' | 'node' | 'python'>('curl');

  const snippets = {
    curl: `curl -X POST "https://api.nomen.ai/v1/generation/" \\
  -H "Authorization: Bearer nm_live_your_api_key_token" \\
  -H "Content-Type: application/json" \\
  -d '{
    "industry": "Artificial Intelligence",
    "context": "A modern agentic AI pair programming tool",
    "target_count": 10,
    "temperature": 0.7
  }'`,
    node: `const axios = require('axios');

const generateNames = async () => {
  try {
    const response = await axios.post(
      'https://api.nomen.ai/v1/generation/',
      {
        industry: 'Artificial Intelligence',
        context: 'A modern agentic AI pair programming tool',
        target_count: 10,
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': 'Bearer nm_live_your_api_key_token',
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('Candidates:', response.data.data);
  } catch (error) {
    console.error('Error generating names:', error.message);
  }
};

generateNames();`,
    python: `import requests

url = "https://api.nomen.ai/v1/generation/"
headers = {
    "Authorization": "Bearer nm_live_your_api_key_token",
    "Content-Type": "application/json"
}
payload = {
    "industry": "Artificial Intelligence",
    "context": "A modern agentic AI pair programming tool",
    "target_count": 10,
    "temperature": 0.7
}

response = requests.post(url, json=payload, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Generated Names:", data["data"])
else:
    print(f"Error: {response.status_code}", response.text)`
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Developer API References</h1>
        <p className="text-sm text-slate-500">Integrate Nomen Brand Intelligence name generation algorithms directly into your product workflows.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center gap-3">
            <Server className="h-6 w-6 text-indigo-600" />
            <CardTitle className="text-sm font-bold">Standard Base URL</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-xs bg-slate-100 dark:bg-slate-800 p-2 rounded block break-all font-mono">
              https://api.nomen.ai/v1
            </code>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-3">
            <Terminal className="h-6 w-6 text-indigo-600" />
            <CardTitle className="text-sm font-bold">Authentication Header</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-xs bg-slate-100 dark:bg-slate-800 p-2 rounded block break-all font-mono">
              Authorization: Bearer nm_live_...
            </code>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-3">
            <Code2 className="h-6 w-6 text-indigo-600" />
            <CardTitle className="text-sm font-bold">Content-Type Format</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-xs bg-slate-100 dark:bg-slate-800 p-2 rounded block break-all font-mono">
              application/json
            </code>
          </CardContent>
        </Card>
      </div>

      {/* Code Snippets Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Code2 className="h-5 w-5 text-indigo-600" />
              Generate Candidate Names Endpoint
            </CardTitle>
            <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md gap-1">
              {(['curl', 'node', 'python'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setActiveTab(lang)}
                  className={`text-xs font-semibold px-3 py-1 rounded ${
                    activeTab === lang
                      ? 'bg-white dark:bg-slate-700 text-slate-850 shadow-sm'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  {lang.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent className="bg-slate-900 rounded-b-lg p-4">
          <pre className="text-xs font-mono text-slate-100 overflow-x-auto whitespace-pre p-2 leading-relaxed">
            {snippets[activeTab]}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
