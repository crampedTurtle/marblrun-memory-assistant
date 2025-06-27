'use client'

import React, { useState, useEffect } from 'react'
import { Plus, Search, Clock, Trash2, Brain } from 'lucide-react'
import { NoteForm } from '../components/NoteForm'
import { SearchBar } from '../components/SearchBar'
import { NoteList } from '../components/NoteList'
import { SearchResults } from '../components/SearchResults'
import { api } from '../lib/api'

interface Note {
  id: number
  content: string
  title?: string
  created_at: string
  updated_at?: string
}

interface SearchResult {
  query: string
  results: Note[]
  total_found: number
  search_time_ms: number
}

export default function HomePage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'notes' | 'search'>('notes')
  const [showNoteForm, setShowNoteForm] = useState(false)

  // Load notes on component mount
  useEffect(() => {
    loadNotes()
  }, [])

  const loadNotes = async () => {
    try {
      setIsLoading(true)
      const response = await api.get('/notes')
      setNotes(response.data)
    } catch (error) {
      console.error('Failed to load notes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateNote = async (noteData: { content: string; title?: string }) => {
    try {
      const response = await api.post('/notes', noteData)
      setNotes(prev => [response.data, ...prev])
      setShowNoteForm(false)
    } catch (error) {
      console.error('Failed to create note:', error)
    }
  }

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults(null)
      return
    }

    try {
      setIsLoading(true)
      const response = await api.post('/query', { query, limit: 10 })
      setSearchResults(response.data)
      setActiveTab('search')
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteNote = async (noteId: number) => {
    try {
      await api.delete(`/notes/${noteId}`)
      setNotes(prev => prev.filter(note => note.id !== noteId))
      if (searchResults) {
        setSearchResults(prev => prev ? {
          ...prev,
          results: prev.results.filter(note => note.id !== noteId)
        } : null)
      }
    } catch (error) {
      console.error('Failed to delete note:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Brain className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">MarblRun</h1>
              <span className="text-sm text-gray-500">Memory Assistant</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowNoteForm(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Add Note</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-white rounded-lg p-1 shadow-sm">
          <button
            onClick={() => setActiveTab('notes')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'notes'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Clock className="h-4 w-4 inline mr-2" />
            Timeline
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'search'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Search className="h-4 w-4 inline mr-2" />
            Search Results
          </button>
        </div>

        {/* Content Area */}
        <div className="space-y-6">
          {activeTab === 'notes' && (
            <NoteList
              notes={notes}
              onDelete={handleDeleteNote}
              isLoading={isLoading}
            />
          )}
          
          {activeTab === 'search' && searchResults && (
            <SearchResults
              results={searchResults}
              onDelete={handleDeleteNote}
            />
          )}
          
          {activeTab === 'search' && !searchResults && (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Search for memories to get started</p>
            </div>
          )}
        </div>
      </main>

      {/* Note Form Modal */}
      {showNoteForm && (
        <NoteForm
          onSubmit={handleCreateNote}
          onCancel={() => setShowNoteForm(false)}
        />
      )}
    </div>
  )
} 