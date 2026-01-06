'use client'

import { useState } from 'react'
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import { TenderCard } from '@/components/tenders/TenderCard'
import { useTenders } from '@/hooks/useTenders'

export default function TendersPage() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [region, setRegion] = useState('')
  const [page, setPage] = useState(1)
  const itemsPerPage = 20

  const { data, loading, error } = useTenders({
    search: search || undefined,
    category: category || undefined,
    region: region || undefined,
    skip: (page - 1) * itemsPerPage,
    limit: itemsPerPage,
  })

  const totalPages = data ? Math.ceil(data.total / itemsPerPage) : 0

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleSearchChange = (value: string) => {
    setSearch(value)
    setPage(1) // Reset to first page on search
  }

  const handleCategoryChange = (value: string) => {
    setCategory(value)
    setPage(1) // Reset to first page on filter change
  }

  const handleRegionChange = (value: string) => {
    setRegion(value)
    setPage(1) // Reset to first page on filter change
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Browse Tenders
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Discover and track business opportunities
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search tenders..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>

          <select
            value={category}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Categories</option>
            <option value="IT">IT & Software</option>
            <option value="Construction">Construction</option>
            <option value="Consulting">Consulting</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Education">Education</option>
          </select>

          <select
            value={region}
            onChange={(e) => handleRegionChange(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Regions</option>
            <option value="North">North</option>
            <option value="South">South</option>
            <option value="East">East</option>
            <option value="West">West</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tenders...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            Found {data.total} tender{data.total !== 1 ? 's' : ''}
            {data.total > itemsPerPage && (
              <span className="ml-2">
                (Page {page} of {totalPages})
              </span>
            )}
          </div>

          {data.items.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <Filter size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No tenders found</p>
              <p className="text-sm text-gray-500 mt-2">Try adjusting your search filters</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {data.items.map((tender) => (
                  <TenderCard key={tender.id} tender={tender} />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2">
                  <button
                    onClick={() => handlePageChange(page - 1)}
                    disabled={page === 1}
                    className="flex items-center gap-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft size={20} />
                    Previous
                  </button>

                  <div className="flex items-center gap-1">
                    {/* Show first page */}
                    {page > 3 && (
                      <>
                        <button
                          onClick={() => handlePageChange(1)}
                          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          1
                        </button>
                        {page > 4 && (
                          <span className="px-2 text-gray-500">...</span>
                        )}
                      </>
                    )}

                    {/* Show pages around current page */}
                    {Array.from({ length: totalPages }, (_, i) => i + 1)
                      .filter(
                        (pageNum) =>
                          pageNum === page ||
                          pageNum === page - 1 ||
                          pageNum === page - 2 ||
                          pageNum === page + 1 ||
                          pageNum === page + 2
                      )
                      .map((pageNum) => (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-3 py-2 border rounded-lg transition-colors ${
                            pageNum === page
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          {pageNum}
                        </button>
                      ))}

                    {/* Show last page */}
                    {page < totalPages - 2 && (
                      <>
                        {page < totalPages - 3 && (
                          <span className="px-2 text-gray-500">...</span>
                        )}
                        <button
                          onClick={() => handlePageChange(totalPages)}
                          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          {totalPages}
                        </button>
                      </>
                    )}
                  </div>

                  <button
                    onClick={() => handlePageChange(page + 1)}
                    disabled={page === totalPages}
                    className="flex items-center gap-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                    <ChevronRight size={20} />
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}
