'use client'

import { Sparkles, Zap } from 'lucide-react'

interface GeneratedContentProps {
  cleanDescription?: string
  highlights?: string
  aiSummary?: string
}

export function GeneratedContent({ cleanDescription, highlights, aiSummary }: GeneratedContentProps) {
  const hasContent = cleanDescription || highlights || aiSummary

  if (!hasContent) return null

  const parseInlineMarkdown = (text: string): (string | JSX.Element)[] => {
    const parts: (string | JSX.Element)[] = []
    let lastIndex = 0

    // Regular expression to match **bold**, *italic*, and other inline formatting
    const regex = /\*\*(.*?)\*\*|\*(.*?)\*|_(.*?)_/g
    let match

    while ((match = regex.exec(text)) !== null) {
      // Add text before match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index))
      }

      // Add formatted text
      if (match[1]) {
        // Bold text **text**
        parts.push(
          <strong key={parts.length} className="font-semibold text-gray-900 dark:text-white">
            {match[1]}
          </strong>
        )
      } else if (match[2]) {
        // Italic text *text*
        parts.push(
          <em key={parts.length} className="italic">
            {match[2]}
          </em>
        )
      } else if (match[3]) {
        // Underline text _text_
        parts.push(
          <u key={parts.length}>
            {match[3]}
          </u>
        )
      }

      lastIndex = regex.lastIndex
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex))
    }

    return parts.length > 0 ? parts : [text]
  }

  const parseMarkdown = (text: string) => {
    const lines = text.split('\n')
    const elements: JSX.Element[] = []
    let listItems: string[] = []

    lines.forEach((line, idx) => {
      const trimmedLine = line.trim()

      // Skip empty lines but handle them for spacing
      if (!trimmedLine) {
        if (listItems.length > 0) {
          // Render accumulated list items
          elements.push(
            <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
              {listItems.map((item, itemIdx) => (
                <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                  {parseInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          listItems = []
        }
        return
      }

      // Handle headers
      if (trimmedLine.startsWith('###')) {
        if (listItems.length > 0) {
          elements.push(
            <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
              {listItems.map((item, itemIdx) => (
                <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                  {parseInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          listItems = []
        }
        const headerText = trimmedLine.replace(/^#+\s/, '')
        elements.push(
          <h4 key={idx} className="text-sm font-bold text-gray-900 dark:text-white mt-4 mb-2">
            {parseInlineMarkdown(headerText)}
          </h4>
        )
      } else if (trimmedLine.startsWith('##')) {
        if (listItems.length > 0) {
          elements.push(
            <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
              {listItems.map((item, itemIdx) => (
                <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                  {parseInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          listItems = []
        }
        const headerText = trimmedLine.replace(/^#+\s/, '')
        elements.push(
          <h3 key={idx} className="text-base font-bold text-gray-900 dark:text-white mt-4 mb-2">
            {parseInlineMarkdown(headerText)}
          </h3>
        )
      } else if (trimmedLine.startsWith('#')) {
        if (listItems.length > 0) {
          elements.push(
            <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
              {listItems.map((item, itemIdx) => (
                <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                  {parseInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          listItems = []
        }
        const headerText = trimmedLine.replace(/^#+\s/, '')
        elements.push(
          <h2 key={idx} className="text-lg font-bold text-gray-900 dark:text-white mt-4 mb-2">
            {parseInlineMarkdown(headerText)}
          </h2>
        )
      }
      // Handle bullet points and list items
      else if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-') || trimmedLine.startsWith('*')) {
        const itemText = trimmedLine.replace(/^[•\-\*]\s/, '').trim()

        // Check if this is a bold-only header (e.g., "- **Header Text**")
        if (itemText.match(/^\*\*.*\*\*$/) || itemText.match(/^__.*__$/)) {
          // Render any accumulated list items first
          if (listItems.length > 0) {
            elements.push(
              <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
                {listItems.map((item, itemIdx) => (
                  <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                    {parseInlineMarkdown(item)}
                  </li>
                ))}
              </ul>
            )
            listItems = []
          }
          // Treat as a bold header, not a list item
          const headerText = itemText.replace(/\*\*|__/g, '')
          elements.push(
            <h4 key={idx} className="text-sm font-bold text-gray-900 dark:text-white mt-4 mb-2">
              {parseInlineMarkdown(headerText)}
            </h4>
          )
        } else {
          listItems.push(itemText)
        }
      }
      // Handle regular paragraphs and plus-prefixed items
      else if (trimmedLine.startsWith('+')) {
        const itemText = trimmedLine.replace(/^\+\s/, '').trim()

        // Check if this is a bold-only header
        if (itemText.match(/^\*\*.*\*\*$/) || itemText.match(/^__.*__$/)) {
          // Render any accumulated list items first
          if (listItems.length > 0) {
            elements.push(
              <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
                {listItems.map((item, itemIdx) => (
                  <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                    {parseInlineMarkdown(item)}
                  </li>
                ))}
              </ul>
            )
            listItems = []
          }
          // Treat as a bold header, not a list item
          const headerText = itemText.replace(/\*\*|__/g, '')
          elements.push(
            <h4 key={idx} className="text-sm font-bold text-gray-900 dark:text-white mt-4 mb-2">
              {parseInlineMarkdown(headerText)}
            </h4>
          )
        } else {
          listItems.push(itemText)
        }
      } else {
        // Regular paragraph
        if (listItems.length > 0) {
          elements.push(
            <ul key={`list-${idx}`} className="list-disc list-inside space-y-1 my-3">
              {listItems.map((item, itemIdx) => (
                <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
                  {parseInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          listItems = []
        }
        elements.push(
          <p key={idx} className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
            {parseInlineMarkdown(trimmedLine)}
          </p>
        )
      }
    })

    // Handle remaining list items
    if (listItems.length > 0) {
      elements.push(
        <ul key="final-list" className="list-disc list-inside space-y-1 my-3">
          {listItems.map((item, itemIdx) => (
            <li key={itemIdx} className="text-sm text-gray-700 dark:text-gray-300">
              {parseInlineMarkdown(item)}
            </li>
          ))}
        </ul>
      )
    }

    return elements
  }

  return (
    <div className="space-y-6">
      {/* AI Summary */}
      {aiSummary && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
              <Sparkles size={24} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Summary</h3>
          </div>
          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
            {aiSummary.split('\n\n').map((paragraph, idx) => (
              <p key={idx}>{paragraph}</p>
            ))}
          </div>
        </div>
      )}

      {/* Clean Description */}
      {cleanDescription && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Description</h3>
          <div className="prose prose-sm dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
            {parseMarkdown(cleanDescription)}
          </div>
        </div>
      )}

      {/* Highlights */}
      {highlights && (
        <div className="bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-100 dark:bg-amber-900/40 rounded-lg">
              <Zap size={24} className="text-amber-600 dark:text-amber-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Key Highlights</h3>
          </div>

          <div className="space-y-2">
            {highlights
              .split('\n')
              .filter((line) => line.trim())
              .map((line, idx) => {
                const cleanLine = line.replace(/^[•\-\*\+]\s/, '').trim()

                return (
                  <div key={idx} className="flex gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex-shrink-0 pt-0.5">
                      <span className="inline-block w-2 h-2 bg-amber-500 dark:bg-amber-400 rounded-full mt-1.5"></span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{parseInlineMarkdown(cleanLine)}</p>
                  </div>
                )
              })}
          </div>
        </div>
      )}
    </div>
  )
}
