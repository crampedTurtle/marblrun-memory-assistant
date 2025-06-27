'use client'

import { Agent } from '@/types'

interface AgentGridProps {
  agents: Agent[]
  onSelectAgent: (agent: Agent) => void
}

const agentIcons = {
  cara: '💬',
  penny: '✍️',
  eva: '📅',
}

const agentColors = {
  cara: 'from-pink-500 to-rose-500',
  penny: 'from-purple-500 to-indigo-500',
  eva: 'from-blue-500 to-cyan-500',
}

export default function AgentGrid({ agents, onSelectAgent }: AgentGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
      {agents.map((agent) => {
        const icon = agentIcons[agent.name as keyof typeof agentIcons] || '🤖'
        const colorClass = agentColors[agent.name as keyof typeof agentColors] || 'from-gray-500 to-gray-600'
        
        return (
          <div
            key={agent.name}
            onClick={() => onSelectAgent(agent)}
            className="agent-card group"
          >
            <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${colorClass} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
              <span className="text-2xl">{icon}</span>
            </div>
            
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {agent.display_name}
            </h3>
            
            <p className="text-gray-600 leading-relaxed">
              {agent.description}
            </p>
            
            <div className="mt-4 flex items-center text-primary-600 font-medium">
              <span>Start chatting</span>
              <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        )
      })}
    </div>
  )
} 