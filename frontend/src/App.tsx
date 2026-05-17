import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

// Auth
import LoginPage from './pages/LoginPage'

// Employee
import EmployeeLayout from './layouts/EmployeeLayout'
import EmployeeDashboard from './pages/employee/Dashboard'
import GoalList from './pages/employee/GoalList'
import GoalCreate from './pages/employee/GoalCreate'
import GoalView from './pages/employee/GoalView'
import GoalEdit from './pages/employee/GoalEdit'
import Achievements from './pages/employee/Achievements'

// Manager
import ManagerLayout from './layouts/ManagerLayout'
import ManagerDashboard from './pages/manager/Dashboard'
import ManagerApprovals from './pages/manager/Approvals'
import ManagerApprovalDetail from './pages/manager/ApprovalDetail'
import ManagerTeam from './pages/manager/Team'
import ManagerEmployeeView from './pages/manager/EmployeeView'
import ManagerCheckin from './pages/manager/Checkin'
import ManagerAnalytics from './pages/manager/Analytics'

// Admin
import AdminLayout from './layouts/AdminLayout'
import AdminDashboard from './pages/admin/Dashboard'
import AdminUsers from './pages/admin/Users'
import AdminCycles from './pages/admin/Cycles'
import AdminSharedGoals from './pages/admin/SharedGoals'
import AdminReports from './pages/admin/Reports'
import AdminAuditLogs from './pages/admin/AuditLogs'
import AdminAnalytics from './pages/admin/Analytics'

function RoleGuard({ role, children }: { role: string | string[]; children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  const allowed = Array.isArray(role) ? role : [role]
  if (!user || !allowed.includes(user.role)) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RootRedirect() {
  const { user, isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (user?.role === 'employee') return <Navigate to="/employee/dashboard" replace />
  if (user?.role === 'manager') return <Navigate to="/manager/dashboard" replace />
  if (user?.role === 'admin') return <Navigate to="/admin/dashboard" replace />
  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<RootRedirect />} />

        {/* Employee */}
        <Route path="/employee" element={<RoleGuard role="employee"><EmployeeLayout /></RoleGuard>}>
          <Route path="dashboard" element={<EmployeeDashboard />} />
          <Route path="goals" element={<GoalList />} />
          <Route path="goals/new" element={<GoalCreate />} />
          <Route path="goals/:id" element={<GoalView />} />
          <Route path="goals/:id/edit" element={<GoalEdit />} />
          <Route path="achievements" element={<Achievements />} />
        </Route>

        {/* Manager */}
        <Route path="/manager" element={<RoleGuard role="manager"><ManagerLayout /></RoleGuard>}>
          <Route path="dashboard" element={<ManagerDashboard />} />
          <Route path="approvals" element={<ManagerApprovals />} />
          <Route path="approvals/:id" element={<ManagerApprovalDetail />} />
          <Route path="team" element={<ManagerTeam />} />
          <Route path="team/:employeeId" element={<ManagerEmployeeView />} />
          <Route path="checkin/:employeeId" element={<ManagerCheckin />} />
          <Route path="analytics" element={<ManagerAnalytics />} />
        </Route>

        {/* Admin */}
        <Route path="/admin" element={<RoleGuard role="admin"><AdminLayout /></RoleGuard>}>
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="cycles" element={<AdminCycles />} />
          <Route path="shared-goals" element={<AdminSharedGoals />} />
          <Route path="reports" element={<AdminReports />} />
          <Route path="audit" element={<AdminAuditLogs />} />
          <Route path="analytics" element={<AdminAnalytics />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
