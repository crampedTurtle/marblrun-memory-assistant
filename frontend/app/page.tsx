'use client'

import { useState, useEffect } from 'react'
import AgentGrid from '@/components/AgentGrid'
import ChatInterface from '@/components/ChatInterface'
import { Agent } from '@/types'

export default function Home() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])

  useEffect(() => {
    // Fetch available agents
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    fetch(`${apiUrl}/api/agents`)
      .then(res => res.json())
      .then(data => setAgents(data.agents))
      .catch(err => console.error('Failed to fetch agents:', err))
  }, [])

  if (selectedAgent) {
    return (
      <ChatInterface 
        agent={selectedAgent} 
        onBack={() => setSelectedAgent(null)} 
      />
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI Assistant Platform
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Choose your AI assistant and start collaborating. Each agent has unique expertise 
          and maintains their own memory to provide personalized assistance.
        </p>
      </div>
      
      <AgentGrid 
        agents={agents} 
        onSelectAgent={setSelectedAgent} 
      />
    </div>
  )
} 