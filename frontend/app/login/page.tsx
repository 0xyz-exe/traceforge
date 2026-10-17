'use client'

import { FormEvent, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { authApi } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [workspaceName, setWorkspaceName] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      if (mode === 'register') {
        await authApi.register({ email, password, full_name: fullName, workspace_name: workspaceName })
      }
      const response = await authApi.login(email, password)
      localStorage.setItem('access_token', response.data.access_token)
      router.replace(searchParams.get('returnTo') || '/')
    } catch (requestError: any) {
      const detail = requestError.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Unable to connect to TraceForge. Check that the backend is running.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen p-8 flex items-center justify-center">
      <div className="w-full max-w-md bg-card border border-border rounded p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">TraceForge</h1>
            <p className="text-muted mt-2">{mode === 'login' ? 'Sign in to your workspace' : 'Create your workspace'}</p>
          </div>
          <Link href="/" className="text-accent hover:underline">Home</Link>
        </div>

        {error && <div className="bg-error/20 border border-error text-error px-4 py-3 rounded mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <label className="block">
                <span className="text-sm text-muted">Full name</span>
                <input required value={fullName} onChange={event => setFullName(event.target.value)} className="mt-1 w-full bg-background border border-border rounded px-3 py-2" />
              </label>
              <label className="block">
                <span className="text-sm text-muted">Workspace name</span>
                <input required value={workspaceName} onChange={event => setWorkspaceName(event.target.value)} className="mt-1 w-full bg-background border border-border rounded px-3 py-2" />
              </label>
            </>
          )}
          <label className="block">
            <span className="text-sm text-muted">Email</span>
            <input required type="email" value={email} onChange={event => setEmail(event.target.value)} className="mt-1 w-full bg-background border border-border rounded px-3 py-2" />
          </label>
          <label className="block">
            <span className="text-sm text-muted">Password</span>
            <input required minLength={8} type="password" value={password} onChange={event => setPassword(event.target.value)} className="mt-1 w-full bg-background border border-border rounded px-3 py-2" />
          </label>
          <button disabled={isSubmitting} className="w-full px-4 py-2 bg-accent text-white rounded hover:opacity-90 disabled:opacity-50">
            {isSubmitting ? 'Working...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <button
          onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
          className="w-full mt-4 text-accent hover:underline text-sm"
        >
          {mode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in'}
        </button>
      </div>
    </main>
  )
}
