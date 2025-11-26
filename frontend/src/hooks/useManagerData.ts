import { useState, useEffect, useCallback } from 'react';
import { getManagerInfo, getManagerTeam } from '../api/client';
import type { ManagerData, ManagerTeam } from '../api/client';

const MANAGER_ID_KEY = 'fpl_manager_id';

export function useManagerData() {
  const [managerId, setManagerId] = useState<string>('');
  const [managerData, setManagerData] = useState<ManagerData | null>(null);
  const [managerTeam, setManagerTeam] = useState<ManagerTeam | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Load saved manager on mount
  useEffect(() => {
    const savedId = localStorage.getItem(MANAGER_ID_KEY);
    if (savedId) {
      setManagerId(savedId);
      loadManagerData(savedId);
    }
  }, []);

  const loadManagerData = useCallback(async (id: string, includeTeam: boolean = true) => {
    setIsLoading(true);
    setError('');

    try {
      const numId = parseInt(id, 10);
      if (isNaN(numId)) {
        throw new Error('Please enter a valid numeric ID');
      }

      const info = await getManagerInfo(numId);
      setManagerData(info);
      localStorage.setItem(MANAGER_ID_KEY, id);

      if (includeTeam) {
        try {
          const team = await getManagerTeam(numId);
          setManagerTeam(team);
        } catch (teamErr) {
          // Team data is optional, don't fail completely
          console.warn('Could not load team data:', teamErr);
        }
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch manager data');
      setManagerData(null);
      setManagerTeam(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadManagerInfo = useCallback(async (id: string) => {
    setIsLoading(true);
    setError('');

    try {
      const numId = parseInt(id, 10);
      if (isNaN(numId)) {
        throw new Error('Please enter a valid numeric ID');
      }

      const info = await getManagerInfo(numId);
      setManagerData(info);
      localStorage.setItem(MANAGER_ID_KEY, id);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch manager data');
      setManagerData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshTeam = useCallback(async () => {
    if (!managerData) return;
    
    setIsLoading(true);
    try {
      const team = await getManagerTeam(managerData.id);
      setManagerTeam(team);
    } catch (err: any) {
      setError(err?.message || 'Failed to refresh team');
    } finally {
      setIsLoading(false);
    }
  }, [managerData]);

  const clearManager = useCallback(() => {
    setManagerData(null);
    setManagerTeam(null);
    setManagerId('');
    setError('');
    localStorage.removeItem(MANAGER_ID_KEY);
  }, []);

  const handleManagerSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!managerId.trim() || isLoading) return;
    await loadManagerInfo(managerId.trim());
  }, [managerId, isLoading, loadManagerInfo]);

  return {
    // State
    managerId,
    setManagerId,
    managerData,
    managerTeam,
    isLoading,
    error,
    
    // Actions
    loadManagerData,
    loadManagerInfo,
    refreshTeam,
    clearManager,
    handleManagerSubmit,
  };
}
