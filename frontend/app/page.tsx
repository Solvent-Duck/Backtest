import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Backtest</h1>
        <p className="text-xl text-gray-600 mb-8">
          See if your interventions work.
        </p>
        
        <div className="space-y-4">
          <Link
            href="/dashboard"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}
