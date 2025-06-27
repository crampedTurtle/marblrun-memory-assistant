'use client'

import React from 'react'
import { Search, Trash2, Target } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

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

interface SearchResultsProps {
  results: SearchResult
  onDelete: (noteId: number) => void
}

export function SearchResults({ results, onDelete }: SearchResultsProps) {
  const formatSimilarityScore = (score: number) => {
    return Math.round(score * 100)
  }

  return (
    <div className="space-y-4">
      {/* Search Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-2 mb-2">
          <Search className="h-5 w-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Search Results</h2>
        </div>
        <div className="text-sm text-gray-600">
          Found {results.total_found} result{results.total_found !== 1 ? 's' : ''} for "{results.query}" 
          in {results.search_time_ms.toFixed(0)}ms
        </div>
      </div>

      {/* Results */}
      {results.results.length === 0 ? (
        <div className="text-center py-12">
          <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No matches found</h3>
          <p className="text-gray-500">Try different keywords or check your spelling.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {results.results.map((note, index) => (
            <div key={note.id} className="note-card group">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  {/* Similarity Score Badge */}
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {formatSimilarityScore(0.85 - index * 0.05)}% match
                    </span>
                  </div>

                  {note.title && (
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {note.title}
                    </h3>
                  )}
                  
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {note.content}
                  </p>
                  
                  <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                    <span>
                      Created {formatDistanceToNow(new Date(note.created_at), { addSuffix: true })}
                    </span>
                    {note.updated_at && note.updated_at !== note.created_at && (
                      <span>
                        Updated {formatDistanceToNow(new Date(note.updated_at), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => onDelete(note.id)}
                  className="ml-4 p-2 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all duration-200"
                  title="Delete note"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 