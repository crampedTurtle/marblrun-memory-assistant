'use client'

import React from 'react'
import { Clock, Trash2, FileText } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface Note {
  id: number
  content: string
  title?: string
  created_at: string
  updated_at?: string
}

interface NoteListProps {
  notes: Note[]
  onDelete: (noteId: number) => void
  isLoading: boolean
}

export function NoteList({ notes, onDelete, isLoading }: NoteListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading notes...</span>
      </div>
    )
  }

  if (notes.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No notes yet</h3>
        <p className="text-gray-500">Start by adding your first note to build your memory bank.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-6">
        <Clock className="h-5 w-5 text-gray-500" />
        <h2 className="text-lg font-semibold text-gray-900">Timeline</h2>
        <span className="text-sm text-gray-500">({notes.length} notes)</span>
      </div>

      <div className="space-y-4">
        {notes.map((note) => (
          <div key={note.id} className="note-card group">
            <div className="flex justify-between items-start">
              <div className="flex-1">
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
    </div>
  )
} 