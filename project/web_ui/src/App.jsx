import React, { useState } from 'react'
import WeeklyPlanner from './WeeklyPlanner'
import Notepad from './Notepad'
import TodaysTodo from './TodaysTodo'
import ChatWidget from './ChatWidget'

function App() {
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleTaskUpdate = () => {
        // Increment trigger to force WeeklyPlanner to re-fetch
        setRefreshTrigger(prev => prev + 1);
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4 font-sans text-gray-900">
            <div className="max-w-[1600px] mx-auto grid grid-cols-12 gap-4 h-[calc(100vh-2rem)]">

                {/* Main Calendar Area */}
                <div className="col-span-12 lg:col-span-9 h-full">
                    <WeeklyPlanner refreshTrigger={refreshTrigger} />
                </div>

                {/* Sidebar */}
                <div className="col-span-12 lg:col-span-3 flex flex-col gap-4 h-full">
                    <div className="h-[35%]">
                        <ChatWidget onTaskUpdate={handleTaskUpdate} />
                    </div>
                    <div className="h-[30%]">
                        <TodaysTodo />
                    </div>
                    <div className="h-[30%]">
                        <Notepad />
                    </div>
                </div>

            </div>
        </div>
    )
}

export default App
