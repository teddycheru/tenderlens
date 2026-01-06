import api from './api'
import type { Tender, TenderFilters, TenderListResponse } from '@/types/tender'

export const tenderApi = {
  async getTenders(filters?: TenderFilters): Promise<TenderListResponse> {
    const response = await api.get('/tenders', { params: filters })
    return response.data
  },

  async getTenderById(id: string): Promise<Tender> {
    const response = await api.get(`/tenders/${id}`)
    return response.data
  },

  async createTender(tender: Partial<Tender>): Promise<Tender> {
    const response = await api.post('/tenders', tender)
    return response.data
  },

  async updateTender(id: string, tender: Partial<Tender>): Promise<Tender> {
    const response = await api.put(`/tenders/${id}`, tender)
    return response.data
  },

  async deleteTender(id: string): Promise<void> {
    await api.delete(`/tenders/${id}`)
  },
}
