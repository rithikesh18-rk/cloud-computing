import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Overview } from './pages/Overview';
import { WorkloadAnalytics } from './pages/WorkloadAnalytics';
import { Predictions } from './pages/Predictions';
import { ResourceOptimization } from './pages/ResourceOptimization';
import { SimulationLab } from './pages/SimulationLab';
import { ExperimentReports } from './pages/ExperimentReports';
import { Settings } from './pages/Settings';
import { ActiveTab } from './types';
import { api } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(true);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  // Check backend health periodically
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.getHealth();
        setIsBackendHealthy(true);
      } catch (err) {
        setIsBackendHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await api.getHealth();
      setIsBackendHealthy(true);
      setRefreshTrigger((prev) => prev + 1);
    } catch (err) {
      setIsBackendHealthy(false);
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  return (
    <div className="flex h-screen bg-dark-bg text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Viewport */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Sticky Header */}
        <Header
          activeTab={activeTab}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          isBackendHealthy={isBackendHealthy}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 overflow-y-auto bg-dark-bg">
          {activeTab === 'overview' && (
            <Overview key={refreshTrigger} onNavigate={setActiveTab} />
          )}
          {activeTab === 'workload' && <WorkloadAnalytics key={refreshTrigger} />}
          {activeTab === 'predictions' && <Predictions key={refreshTrigger} />}
          {activeTab === 'optimization' && <ResourceOptimization key={refreshTrigger} />}
          {activeTab === 'simulation' && <SimulationLab key={refreshTrigger} />}
          {activeTab === 'reports' && <ExperimentReports key={refreshTrigger} />}
          {activeTab === 'settings' && <Settings key={refreshTrigger} />}
        </main>
      </div>
    </div>
  );
};

export default App;
