import api from './api'

export interface UserPreferences {
  id: string
  user_id: string
  email_notifications: boolean
  new_tender_alerts: boolean
  deadline_reminders: boolean
  weekly_digest: boolean
  language: string
  timezone: string
  date_format: string
  created_at: string
  updated_at: string
}

export interface UserPreferencesUpdate {
  email_notifications?: boolean
  new_tender_alerts?: boolean
  deadline_reminders?: boolean
  weekly_digest?: boolean
  language?: string
  timezone?: string
  date_format?: string
}

export const preferencesApi = {
  async getPreferences(): Promise<UserPreferences> {
    const response = await api.get('/users/me/preferences')
    return response.data
  },

  async updatePreferences(preferences: UserPreferencesUpdate): Promise<UserPreferences> {
    const response = await api.put('/users/me/preferences', preferences)
    return response.data
  },
}

export const userApi = {
  async updateProfile(data: { full_name?: string; email?: string; phone?: string }) {
    const response = await api.put('/users/me', data)
    return response.data
  },

  async changePassword(currentPassword: string, newPassword: string) {
    const response = await api.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },
}
