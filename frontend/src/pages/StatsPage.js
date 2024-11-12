import React, { useEffect, useState } from 'react'
import TeamStatsDashboard from '../components/TeamStatsDashboard'

const StatsPage = () => {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const passResponse = await fetch('/data/player_stats_pass.csv')
        const defResponse = await fetch('/data/player_stats_def.csv')
        const recResponse = await fetch('/data/player_stats_rec.csv')
        const rushResponse = await fetch('/data/player_stats_rush.csv')

        const passText = await passResponse.text()
        const defText = await defResponse.text()
        const recText = await recResponse.text()
        const rushText = await rushResponse.text()

        setDocuments([
          { source: '/data/player_stats_pass.csv', document_content: passText },
          { source: '/data/player_stats_def.csv', document_content: defText },
          { source: '/data/player_stats_rec.csv', document_content: recText },
          { source: '/data/player_stats_rush.csv', document_content: rushText },
        ])
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4 text-blue-600 dark:text-blue-400">
        Team Statistics Dashboard
      </h1>
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600 dark:border-blue-400"></div>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <TeamStatsDashboard documents={documents} />
        </div>
      )}
    </div>
  )
}

export default StatsPage