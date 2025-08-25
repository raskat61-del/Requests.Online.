import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from 'react-query'
import { useForm } from 'react-hook-form'
import { projectsAPI } from '../lib/api'
import { ArrowLeft, Save } from 'lucide-react'
import { toast } from 'react-toastify'

interface CreateProjectFormData {
  name: string
  description: string
  status: string
}

export const CreateProjectPage = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateProjectFormData>({
    defaultValues: {
      status: 'draft',
    },
  })

  const createProjectMutation = useMutation(projectsAPI.createProject, {
    onSuccess: (data) => {
      queryClient.invalidateQueries('projects')
      toast.success('Project created successfully!')
      navigate(`/projects/${data.id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create project')
    },
  })

  const onSubmit = (data: CreateProjectFormData) => {
    createProjectMutation.mutate(data)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/projects')}
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Create New Project</h1>
          <p className="text-gray-600 mt-1">
            Set up a new analytics project to collect and analyze data
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Project Name *
          </label>
          <input
            {...register('name', {
              required: 'Project name is required',
              minLength: {
                value: 3,
                message: 'Project name must be at least 3 characters',
              },
              maxLength: {
                value: 100,
                message: 'Project name must be less than 100 characters',
              },
            })}
            type="text"
            className="input-field"
            placeholder="Enter project name (e.g., 'SaaS Market Research 2024')"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            {...register('description', {
              maxLength: {
                value: 500,
                message: 'Description must be less than 500 characters',
              },
            })}
            rows={4}
            className="input-field resize-none"
            placeholder="Describe your project goals, target audience, and what insights you're looking for..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Optional: Provide details about your project to help with analysis
          </p>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Initial Status
          </label>
          <select
            {...register('status')}
            className="input-field"
          >
            <option value="draft">Draft - Still planning</option>
            <option value="active">Active - Ready to start collecting data</option>
            <option value="paused">Paused - Will start later</option>
          </select>
          <p className="mt-1 text-sm text-gray-500">
            You can change the status later from the project page
          </p>
        </div>

        {/* Project features info */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">What you can do with this project:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Collect data from Google, Yandex, Telegram, VK, Reddit</li>
            <li>• Analyze sentiment and identify pain points</li>
            <li>• Cluster topics and find patterns</li>
            <li>• Generate comprehensive reports (PDF, Excel)</li>
            <li>• Track progress and manage multiple search tasks</li>
          </ul>
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-4 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate('/projects')}
            className="btn-secondary"
            disabled={createProjectMutation.isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary flex items-center"
            disabled={createProjectMutation.isLoading}
          >
            {createProjectMutation.isLoading ? (
              <>
                <div className="loading-spinner mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Create Project
              </>
            )}
          </button>
        </div>
      </form>

      {/* Help section */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Need Help Getting Started?</h3>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-primary-600 text-sm font-medium">1</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Create your project</p>
              <p className="text-sm text-gray-600">Give it a descriptive name and set the initial status</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-primary-600 text-sm font-medium">2</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Add search tasks</p>
              <p className="text-sm text-gray-600">Define keywords and queries to collect relevant data</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-primary-600 text-sm font-medium">3</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Analyze and generate reports</p>
              <p className="text-sm text-gray-600">Let AI analyze the data and create insights reports</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}