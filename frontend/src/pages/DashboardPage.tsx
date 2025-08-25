import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { projectsAPI } from '../lib/api'
import { 
  FolderOpen, 
  FileText, 
  TrendingUp, 
  Clock,
  Plus,
  BarChart3,
  Search,
  Users
} from 'lucide-react'

export const DashboardPage = () => {
  const { data: projects, isLoading } = useQuery(
    'projects',
    () => projectsAPI.getProjects({ limit: 5 }),
    {
      refetchOnWindowFocus: false,
    }
  )

  // Calculate dashboard statistics
  const totalProjects = projects?.length || 0
  const activeProjects = projects?.filter(p => p.status === 'active').length || 0
  const totalTasks = projects?.reduce((sum, p) => sum + p.stats.total_tasks, 0) || 0
  const completedTasks = projects?.reduce((sum, p) => sum + p.stats.completed_tasks, 0) || 0
  const totalReports = projects?.reduce((sum, p) => sum + p.stats.total_reports, 0) || 0

  const stats = [
    {
      name: 'Total Projects',
      value: totalProjects,
      icon: FolderOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Active Projects',
      value: activeProjects,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Total Tasks',
      value: totalTasks,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Reports Generated',
      value: totalReports,
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8 text-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Welcome to Analytics Bot</h1>
        <p className="text-primary-100 mb-4">
          Discover insights and pain points from multiple data sources to drive your SaaS development.
        </p>
        <Link
          to="/projects/new"
          className="inline-flex items-center px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Project
        </Link>
      </div>

      {/* Statistics cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent projects */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
            <Link
              to="/projects"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View all
            </Link>
          </div>
          
          {projects && projects.length > 0 ? (
            <div className="space-y-3">
              {projects.slice(0, 5).map((project) => (
                <div key={project.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <FolderOpen className="w-4 h-4 text-primary-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{project.name}</p>
                      <p className="text-xs text-gray-500">
                        {project.stats.total_tasks} tasks • {project.stats.total_reports} reports
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      project.status === 'active' 
                        ? 'bg-green-100 text-green-800'
                        : project.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {project.status}
                    </span>
                    <Link
                      to={`/projects/${project.id}`}
                      className="text-primary-600 hover:text-primary-700"
                    >
                      <BarChart3 className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6">
              <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">No projects yet</p>
              <Link
                to="/projects/new"
                className="btn-primary inline-flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Project
              </Link>
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/projects/new"
              className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="p-2 bg-blue-100 rounded-lg">
                <Plus className="w-4 h-4 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Create New Project</p>
                <p className="text-xs text-gray-500">Start analyzing data from multiple sources</p>
              </div>
            </Link>
            
            <Link
              to="/reports"
              className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="w-4 h-4 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">View Reports</p>
                <p className="text-xs text-gray-500">Access your generated analysis reports</p>
              </div>
            </Link>
            
            <div className="flex items-center p-3 bg-gray-50 rounded-lg">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Search className="w-4 h-4 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Data Sources</p>
                <p className="text-xs text-gray-500">Google, Yandex, Telegram, VK, Reddit, Forums</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress overview */}
      {totalTasks > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h2>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Tasks Completed</span>
            <span className="text-sm font-medium text-gray-900">
              {completedTasks} / {totalTasks}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(completedTasks / totalTasks) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}