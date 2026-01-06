/**
 * Utility functions for handling API errors
 */

interface ValidationError {
  type: string
  loc: string[]
  msg: string
  input?: any
  ctx?: any
  url?: string
}

/**
 * Extract a user-friendly error message from API error response
 */
export function getErrorMessage(error: any): string {
  // Check if it's a validation error array
  if (Array.isArray(error.response?.data?.detail)) {
    const errors = error.response.data.detail as ValidationError[]
    // Return the first error message
    if (errors.length > 0) {
      return errors[0].msg
    }
  }

  // Check if it's a single error message (string)
  if (typeof error.response?.data?.detail === 'string') {
    return error.response.data.detail
  }

  // Check for other error formats
  if (error.response?.data?.message) {
    return error.response.data.message
  }

  if (error.message) {
    return error.message
  }

  return 'An error occurred. Please try again.'
}
