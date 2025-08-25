import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Link } from 'react-router-dom'
import { projectsAPI, ProjectWithStats } from '../lib/api'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical,
  FolderOpen,
  Clock,
  FileText,
  BarChart3,
  Trash2,
  Edit
} from 'lucide-react'
import { toast } from 'react-toastify'

export const ProjectsPage = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const queryClient = useQueryClient()

  const { data: projects, isLoading, error } = useQuery(
    ['projects', { search: searchTerm, status: statusFilter }],
    () => projectsAPI.getProjects({
      status: statusFilter === 'all' ? undefined : statusFilter
    }),
    {
      refetchOnWindowFocus: false,
    }
  )

  const deleteProjectMutation = useMutation(projectsAPI.deleteProject, {
    onSuccess: () => {
      queryClient.invalidateQueries('projects')
      toast.success('Project deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project')
    },
  })

  const handleDeleteProject = async (projectId: number) => {
    if (window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      deleteProjectMutation.mutate(projectId)
    }
  }

  // Filter projects based on search term
  const filteredProjects = projects?.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8 text-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load projects</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-1">
            Manage your analytics projects and track their progress
          </p>
        </div>
        <Link
          to="/projects/new"
          className="btn-primary inline-flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field w-40"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="paused">Paused</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </div>

      {/* Projects grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onDelete={handleDeleteProject}
              getStatusColor={getStatusColor}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-600 mb-6">
            {searchTerm || statusFilter !== 'all'
              ? 'Try adjusting your search or filter criteria'
              : 'Get started by creating your first analytics project'}
          </p>
          <Link
            to="/projects/new"
            className="btn-primary inline-flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Project
          </Link>
        </div>
      )}
    </div>
  )
}

interface ProjectCardProps {
  project: ProjectWithStats
  onDelete: (id: number) => void
  getStatusColor: (status: string) => string
}

const ProjectCard = ({ project, onDelete, getStatusColor }: ProjectCardProps) => {
  const [showMenu, setShowMenu] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            <Link
              to={`/projects/${project.id}`}
              className="hover:text-primary-600 transition-colors"
            >
              {project.name}
            </Link>
          </h3>
          <p className="text-gray-600 text-sm line-clamp-2">
            {project.description || 'No description provided'}
          </p>
        </div>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <MoreVertical className="w-4 h-4" />
          </button>
          {showMenu && (
            <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
              <Link
                to={`/projects/${project.id}`}
                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                onClick={() => setShowMenu(false)}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                View Details
              </Link>
              <button
                onClick={() => {
                  setShowMenu(false)
                  // Handle edit - could navigate to edit page
                }}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit Project
              </button>
              <button
                onClick={() => {
                  setShowMenu(false)
                  onDelete(project.id)
                }}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(project.status)}`}>
          {project.status}
        </span>
        <div className="text-xs text-gray-500">
          Created {formatDate(project.created_at)}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full mx-auto mb-1">
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-sm font-medium text-gray-900">{project.stats.total_tasks}</div>
          <div className="text-xs text-gray-500">Tasks</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full mx-auto mb-1">
            <BarChart3 className="w-4 h-4 text-green-600" />
          </div>
          <div className="text-sm font-medium text-gray-900">{project.stats.total_data_collected}</div>
          <div className="text-xs text-gray-500">Data</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-full mx-auto mb-1">
            <FileText className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-sm font-medium text-gray-900">{project.stats.total_reports}</div>
          <div className="text-xs text-gray-500">Reports</div>
        </div>
      </div>

      {project.stats.total_tasks > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600">Progress</span>
            <span className="text-xs text-gray-900">
              {Math.round((project.stats.completed_tasks / project.stats.total_tasks) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
              style={{ 
                width: `${(project.stats.completed_tasks / project.stats.total_tasks) * 100}%` 
              }}
            />
          </div>
        </div>
      )}

      <Link
        to={`/projects/${project.id}`}
        className="btn-secondary w-full text-center"
      >
        View Project
      </Link>
    </div>
  )
}