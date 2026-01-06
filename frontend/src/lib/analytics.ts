import api from './api'

export interface SummaryStats {
  total_tenders: number
  upcoming_tenders: number
  recent_tenders: number
  average_budget: number
}

export const analyticsApi = {
  async getSummaryStats(): Promise<SummaryStats> {
    const response = await api.get('/analytics/summary')
    return response.data
  },
}
