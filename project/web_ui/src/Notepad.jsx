import React, { useState, useEffect } from 'react';

export default function Notepad() {
    const [note, setNote] = useState("");

    useEffect(() => {
        const saved = localStorage.getItem("planner_notepad");
        if (saved) setNote(saved);
    }, []);

    const handleChange = (e) => {
        const val = e.target.value;
        setNote(val);
        localStorage.setItem("planner_notepad", val);
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
            <div className="p-3 border-b bg-gray-50 font-semibold text-gray-700 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                Notepad
            </div>
            <textarea
                className="flex-1 w-full p-4 resize-none outline-none text-sm leading-relaxed text-gray-700"
                placeholder="Type your quick notes here..."
                value={note}
                onChange={handleChange}
            />
        </div>
    );
}
