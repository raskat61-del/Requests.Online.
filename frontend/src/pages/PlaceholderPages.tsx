import { useParams } from 'react-router-dom'

export const ProjectDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  
  return (
    <div className="text-center py-12">
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">
        Project Detail Page
      </h1>
      <p className="text-gray-600">
        Project ID: {id}
      </p>
      <p className="text-gray-500 mt-2">
        This page will show detailed project information, search tasks, analysis results, and data management features.
      </p>
    </div>
  )
}

export const ReportsPage = () => {
  return (
    <div className="text-center py-12">
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">
        Reports Page
      </h1>
      <p className="text-gray-500">
        This page will show all generated reports with download options and report management features.
      </p>
    </div>
  )
}

export const SettingsPage = () => {
  return (
    <div className="text-center py-12">
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">
        Settings Page
      </h1>
      <p className="text-gray-500">
        This page will contain user settings, API configurations, subscription management, and preferences.
      </p>
    </div>
  )
}