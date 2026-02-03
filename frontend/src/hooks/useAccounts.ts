import { useCallback } from 'react'
import { useAccountsState, useSetAccounts } from '../store'
import type { AccountSummary } from '../types/api'
import { deleteApi, fetchApi, postApi, putApi } from './useApiClient'

interface AccountPayload {
  name: string
  provider_id: string
  model: string
  api_key?: string
  base_url?: string
  description?: string
  is_default?: boolean
}

interface AccountUpdatePayload {
  provider_id: string
  model: string
  api_key?: string
  base_url?: string
  description?: string
  is_default?: boolean
}

export function useAccounts() {
  const accounts = useAccountsState()
  const setAccounts = useSetAccounts()

  const fetchAccounts = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<AccountSummary[]>('/accounts')
      setAccounts(response)
    } catch (error) {
      console.error('Failed to fetch accounts:', error)
      throw error
    }
  }, [setAccounts])

  const createAccount = useCallback(async (payload: AccountPayload): Promise<AccountSummary> => {
    try {
      const created = await postApi<AccountSummary>('/accounts', payload)
      setAccounts([created, ...accounts.filter((account) => account.name !== created.name)])
      return created
    } catch (error) {
      console.error('Failed to create account:', error)
      throw error
    }
  }, [accounts, setAccounts])

  const updateAccount = useCallback(async (name: string, payload: AccountUpdatePayload): Promise<AccountSummary> => {
    try {
      const updated = await putApi<AccountSummary>(`/accounts/${name}`, payload)
      setAccounts(accounts.map((account) => (account.name === name ? updated : account)))
      return updated
    } catch (error) {
      console.error('Failed to update account:', error)
      throw error
    }
  }, [accounts, setAccounts])

  const deleteAccount = useCallback(async (name: string): Promise<void> => {
    try {
      await deleteApi(`/accounts/${name}`)
      setAccounts(accounts.filter((account) => account.name !== name))
    } catch (error) {
      console.error('Failed to delete account:', error)
      throw error
    }
  }, [accounts, setAccounts])

  const setDefaultAccount = useCallback(async (name: string): Promise<AccountSummary> => {
    try {
      const updated = await postApi<AccountSummary>(`/accounts/${name}/default`)
      const refreshed = accounts.map((account) => ({
        ...account,
        is_default: account.name === name,
      }))
      setAccounts(refreshed.map((account) => (account.name === name ? updated : account)))
      return updated
    } catch (error) {
      console.error('Failed to set default account:', error)
      throw error
    }
  }, [accounts, setAccounts])

  return {
    accounts,
    fetchAccounts,
    createAccount,
    updateAccount,
    deleteAccount,
    setDefaultAccount,
  }
}
